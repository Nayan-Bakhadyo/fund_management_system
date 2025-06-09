from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Max
from .models import AuthorizedUser, UserTransaction, UserNAV, NAVRecord
import random
from django import template
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils import timezone

# Create your views here.

def home(request):
    return render(request, "mainapp/home.html")

@login_required
def send_verification_code(request):
    code = random.randint(100000, 999999)
    request.session['verification_code'] = str(code)
    request.session['verification_email'] = request.user.email
    send_mail(
        'Your Verification Code',
        f'Your verification code is: {code}',
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
        fail_silently=False,
    )
    return redirect('verify_email')

@login_required
def verify_email(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        if code == request.session.get('verification_code'):
            email = request.session.get('verification_email')
            AuthorizedUser.objects.get_or_create(email=email, defaults={'role': 'user'})
            return render(request, 'mainapp/verification_success.html')
        else:
            return render(request, 'mainapp/verify_email.html', {'error': 'Invalid code'})
    return render(request, 'mainapp/verify_email.html')

register = template.Library()

@register.filter
def is_authorized(email):
    return AuthorizedUser.objects.filter(email=email).exists()


def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def fundmanager_dashboard(request):
    try:
        authorized_user = AuthorizedUser.objects.get(email=request.user.email)
        if authorized_user.role == 'fund_manager':
            authorized_users = AuthorizedUser.objects.all()
            return render(request, 'mainapp/fundmanager_dashboard.html', {'authorized_users': authorized_users})
        else:
            return redirect('home')
    except AuthorizedUser.DoesNotExist:
        return redirect('home')

@login_required
def add_transaction(request):
    try:
        authorized_user = AuthorizedUser.objects.get(email=request.user.email)
        if authorized_user.role != 'fund_manager':
            return JsonResponse({"success": False, "error": "Unauthorized"})
    except AuthorizedUser.DoesNotExist:
        return JsonResponse({"success": False, "error": "Unauthorized"})

    if request.method == 'POST':
        email = request.POST.get('authorized_email')
        amount = float(request.POST.get('amount'))
        action_type = request.POST.get('action_type')
        transaction_image = request.FILES.get('transaction_image')  # <-- Get the uploaded image

        user = AuthorizedUser.objects.get(email=email)
        nav, _ = UserNAV.objects.get_or_create(authorized_user=user)

        # Get latest NAVRecord unit_cost
        latest_nav_record = NAVRecord.objects.order_by('-date_time').first()
        unit_cost = float(latest_nav_record.unit_cost) if latest_nav_record else 10.0

        if action_type == 'deposit':
            a = float(nav.available_credit_amount)
            purchase_nav = int((amount + a) // unit_cost)
            remaining_credit = (amount + a) - (purchase_nav * unit_cost)

            try:
                with transaction.atomic():
                    nav.available_unit += purchase_nav
                    nav.available_credit_amount = remaining_credit
                    nav.save()
                    UserTransaction.objects.create(
                        authorized_user=user,
                        transaction_type=action_type,
                        unit_cost=unit_cost,
                        purchase_initiated_amount=amount,
                        purchase_unit=purchase_nav,
                        remaining_credit=remaining_credit,
                        transaction_image=transaction_image  # <-- Save the image
                    )
                return JsonResponse({
                    "success": True,
                    "transaction_type": "Deposit",
                    "amount": amount,
                    "unit_purchased": purchase_nav,
                    "unit_cost": unit_cost,
                    "user_email": user.email
                })
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)})

        elif action_type == 'withdrawal':
            available_unit = float(nav.available_unit)
            available_credit = float(nav.available_credit_amount)
            max_withdrawable = (available_unit * unit_cost) + available_credit

            if amount > max_withdrawable:
                return JsonResponse({"success": False, "error": "Withdrawal amount exceeds available balance."})
            else:
                credit_used = min(amount, available_credit)
                amount_left = amount - credit_used
                units_to_withdraw = int(amount_left // unit_cost) + 1 if amount_left > 0 else 0
                remaining_credit = available_credit - credit_used + (units_to_withdraw * unit_cost - amount_left if amount_left > 0 else 0)

                try:
                    with transaction.atomic():
                        nav.available_unit -= units_to_withdraw
                        nav.available_credit_amount = remaining_credit
                        nav.save()
                        UserTransaction.objects.create(
                            authorized_user=user,
                            transaction_type=action_type,
                            unit_cost=unit_cost,
                            purchase_initiated_amount=amount,
                            purchase_unit=-units_to_withdraw,
                            remaining_credit=remaining_credit,
                            transaction_image=transaction_image  # <-- Save the image
                        )
                    return JsonResponse({
                        "success": True,
                        "transaction_type": "Withdrawal",
                        "amount": amount,
                        "unit_purchased": -units_to_withdraw,
                        "unit_cost": unit_cost,
                        "user_email": user.email
                    })
                except Exception as e:
                    return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request."})

@login_required
def add_transaction_form(request):
    authorized_users = AuthorizedUser.objects.all()
    html = render_to_string('mainapp/add_transaction_form.html', {'authorized_users': authorized_users})
    return JsonResponse({'html': html})

@login_required
def view_transactions(request):
    email = request.GET.get('filter_email')
    authorized_users = AuthorizedUser.objects.all()
    if email:
        transactions = UserTransaction.objects.filter(authorized_user__email=email).order_by('-date_time')
    else:
        transactions = UserTransaction.objects.all().order_by('-date_time')
    html = render_to_string(
        'mainapp/view_transactions.html',
        {'transactions': transactions, 'authorized_users': authorized_users, 'selected_email': email}
    )
    return JsonResponse({'html': html})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def user_dashboard(request):
    return render(request, 'mainapp/user_dashboard.html')

@login_required
def portfolio(request):
    # Fetch total unit balance for the user
    user_nav = UserNAV.objects.filter(authorized_user__email=request.user.email).first()
    total_units = user_nav.available_unit if user_nav else 0

    # Fetch latest NAV record
    latest_nav_record = NAVRecord.objects.order_by('-date_time').first()
    nav = latest_nav_record.unit_cost if latest_nav_record else 0
    nav_date = latest_nav_record.date_time.strftime('%Y-%m-%d') if latest_nav_record else 'N/A'

    # Calculate total amount
    total_amount = total_units * nav

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'mainapp/portfolio.html',
            {
                'total_units': total_units,
                'nav': nav,
                'nav_date': nav_date,
                'total_amount': total_amount,
            },
            request=request
        )
        return HttpResponse(html)
    return render(
        request,
        'mainapp/portfolio.html',
        {
            'total_units': total_units,
            'nav': nav,
            'nav_date': nav_date,
            'total_amount': total_amount,
        }
    )
