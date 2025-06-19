from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_GET
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.db.models import Max, Sum
from .models import AuthorizedUser, UserRecurringPayment, UserTransaction, UserNAV, NAVRecord, UserBankDetail, InvestmentCategory, FirmInvestment, TotalCapitalRecord, InvestmentTransaction, UserTransactionUpload
import random
from django import template
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from decimal import Decimal
import json
from django.core.serializers.json import DjangoJSONEncoder

def update_nav_record():
    latest_capital = TotalCapitalRecord.objects.latest('id')
    if not latest_capital or latest_capital.total_circulating_unit == 0:
        return None  # Avoid division by zero or missing data

    nav = (latest_capital.invested_capital + latest_capital.available_capital) / latest_capital.total_circulating_unit
    nav_record = NAVRecord.objects.create(unit_cost=nav)
    return nav_record

def mask_email(email):
    try:
        local, domain = email.split('@')
        if len(local) <= 2:
            masked_local = local[0] + '*' * (len(local)-1)
        else:
            masked_local = local[0] + '*' * (len(local)-2) + local[-1]
        return masked_local + '@' + domain
    except Exception:
        return email

# Create your views here.

def home(request):
    if request.user.is_authenticated:
        try:
            authorized_user = AuthorizedUser.objects.get(email=request.user.email)
            if authorized_user.role == 'fund_manager':
                return redirect('fundmanager_dashboard')
            else:
                return redirect('user_dashboard')
        except AuthorizedUser.DoesNotExist:
            return redirect('verify_email')
    return render(request, "mainapp/home.html")

@login_required
def send_verification_code(request):
    import random
    code = random.randint(100000, 999999)
    request.session['verification_code'] = str(code)
    request.session['verification_email'] = request.user.email

    subject = 'Your BE Investment Firm Verification Code'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [request.user.email]

    # HTML content
    html_content = f"""
    <div style="max-width:480px;margin:0 auto;padding:24px 18px;background:#fffbe6;border-radius:12px;
        border:1.5px solid #bfa14a;font-family:sans-serif;">
        <div style="text-align:center;margin-bottom:18px;">
            <img src="https://drive.google.com/file/d/1gCOmiNtJKrWQq5kmHOeQpKxaZPFdjIGc/view?usp=sharing" alt="BE Logo" style="width:56px;height:56px;border-radius:10px;">
        </div>
        <h2 style="color:#bfa14a;text-align:center;margin-bottom:10px;">Email Verification</h2>
        <p style="color:#14213d;text-align:center;font-size:1.1rem;margin-bottom:18px;">
            Welcome to <b>BE Investment Firm</b>!<br>
            Please use the code below to verify your email address.
        </p>
        <div style="background:#fff8e1;border-radius:8px;padding:18px 0;margin:18px 0;text-align:center;">
            <span style="font-size:2rem;letter-spacing:6px;color:#14213d;font-weight:700;">{code}</span>
        </div>
        <ul style="color:#6c757d;font-size:0.98rem;margin-bottom:18px;">
            <li>This code is valid for 10 minutes.</li>
            <li>Do not share your code with anyone.</li>
            <li>If you did not request this, please ignore this email.</li>
        </ul>
        <div style="text-align:center;color:#888;font-size:0.95rem;">
            Need help? Contact <a href="mailto:beinvestmentfirm@gmail.com" style="color:#bfa14a;">beinvestmentfirm@gmail.com</a>
        </div>
    </div>
    """

    # Plain text fallback
    text_content = f"""Your BE Investment Firm verification code is: {code}
This code is valid for 10 minutes. Do not share your code with anyone.
If you did not request this, please ignore this email.
Contact beinvestmentfirm@gmail.com for help."""

    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)


@login_required
def verify_email(request):
    is_authorized = AuthorizedUser.objects.filter(email=request.user.email).exists()
    error = None

    # Automatically send code if not authorized and not already sent in this session
    if not is_authorized and not request.session.get('verification_code_sent'):
        code = random.randint(100000, 999999)
        request.session['verification_code'] = str(code)
        request.session['verification_email'] = request.user.email

        subject = 'Your BE Investment Firm Verification Code'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [request.user.email]

        html_content = f"""
        <div style="max-width:480px;margin:0 auto;padding:24px 18px;background:#fffbe6;border-radius:12px;
            border:1.5px solid #bfa14a;font-family:sans-serif;">
            <div style="text-align:center;margin-bottom:18px;">
                <img src="https://yourdomain.com/static/mainapp/assets/be_logo.png" alt="BE Logo" style="width:56px;height:56px;border-radius:10px;">
            </div>
            <h2 style="color:#bfa14a;text-align:center;margin-bottom:10px;">Email Verification</h2>
            <p style="color:#14213d;text-align:center;font-size:1.1rem;margin-bottom:18px;">
                Welcome to <b>BE Investment Firm</b>!<br>
                Please use the code below to verify your email address.
            </p>
            <div style="background:#fff8e1;border-radius:8px;padding:18px 0;margin:18px 0;text-align:center;">
                <span style="font-size:2rem;letter-spacing:6px;color:#14213d;font-weight:700;">{code}</span>
            </div>
            <ul style="color:#6c757d;font-size:0.98rem;margin-bottom:18px;">
                <li>This code is valid for 10 minutes.</li>
                <li>Do not share your code with anyone.</li>
                <li>If you did not request this, please ignore this email.</li>
            </ul>
            <div style="text-align:center;color:#888;font-size:0.95rem;">
                Need help? Contact <a href="mailto:beinvestmentfirm@gmail.com" style="color:#bfa14a;">beinvestmentfirm@gmail.com</a>
            </div>
        </div>
        """

        text_content = f"""Your BE Investment Firm verification code is: {code}
    This code is valid for 10 minutes. Do not share your code with anyone.
    If you did not request this, please ignore this email.
    Contact beinvestmentfirm@gmail.com for help."""

        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        request.session['verification_code_sent'] = True

    if request.method == 'POST' and not is_authorized:
        code = request.POST.get('code')
        if code == request.session.get('verification_code'):
            email = request.session.get('verification_email')
            AuthorizedUser.objects.get_or_create(email=email, defaults={'role': 'user'})
            # Clean up session
            request.session.pop('verification_code', None)
            request.session.pop('verification_email', None)
            request.session.pop('verification_code_sent', None)
            return render(request, 'mainapp/verification_success.html')
        else:
            error = 'Invalid code'
    masked_email = mask_email(request.user.email)
    context = {
        'error': error,
        'is_authorized': is_authorized,
        'masked_email': masked_email,
    }
    return render(request, 'mainapp/verify_email.html', context)

register = template.Library()

@register.filter
def is_authorized(email):
    return AuthorizedUser.objects.filter(email=email).exists()


def logout_view(request):
    logout(request)
    return redirect('home')

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
        amount = Decimal(request.POST.get('amount'))
        action_type = request.POST.get('action_type')
        transaction_image = request.FILES.get('transaction_image')
        description = request.POST.get('description', '')  # <-- Get description from form

        user = AuthorizedUser.objects.get(email=email)
        nav, _ = UserNAV.objects.get_or_create(authorized_user=user)

        latest_nav_record = NAVRecord.objects.latest('id')
        unit_cost = Decimal(str(latest_nav_record.unit_cost)) if latest_nav_record else Decimal('10.0')

        if action_type == 'deposit':
            a = nav.available_credit_amount  # Should be Decimal
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
                        transaction_image=transaction_image,
                        description=description  # <-- Save description
                    )

                    # 1. Retrieve the latest TotalCapitalRecord (or create one if none exists)
                    latest_capital = TotalCapitalRecord.objects.order_by('-date_time').first()
                    if not latest_capital:
                        # If no record exists, initialize with zeros
                        latest_capital = TotalCapitalRecord.objects.create(
                            total_capital=0,
                            invested_capital=0,
                            available_capital=0,
                            total_circulating_unit=0
                        )

                    # 2. Update available_capital based on transaction type
                    if action_type == 'deposit':
                        new_available_capital = latest_capital.available_capital + amount
                        new_total_circulating_unit = latest_capital.total_circulating_unit + purchase_nav
                        new_total_capital = latest_capital.total_capital + amount
                    elif action_type == 'withdrawal':
                        new_available_capital = latest_capital.available_capital - amount
                        new_total_circulating_unit = latest_capital.total_circulating_unit + purchase_nav  # purchase_nav is negative for withdrawal
                        new_total_capital = latest_capital.total_capital - amount


                    # 4. Create a new TotalCapitalRecord with updated values
                    TotalCapitalRecord.objects.create(
                        total_capital= new_total_capital,
                        invested_capital=latest_capital.invested_capital,  # or update as needed
                        available_capital=new_available_capital,
                        total_circulating_unit=new_total_circulating_unit
                    )

                update_nav_record()  # <-- Call after atomic block
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
            available_unit = Decimal(str(nav.available_unit))
            available_credit = Decimal(str(nav.available_credit_amount))
            unit_cost = Decimal(str(unit_cost))
            amount = Decimal(request.POST.get('amount'))

            max_withdrawable = (available_unit * unit_cost) + available_credit

            if amount > max_withdrawable:
                return JsonResponse({"success": False, "error": "Withdrawal amount exceeds available balance."})
            else:
                credit_used = min(amount, available_credit)
                amount_left = amount - credit_used
                units_to_withdraw = int(amount_left // unit_cost) + (1 if amount_left % unit_cost != 0 else 0) if amount_left > 0 else 0
                purchase_nav = -units_to_withdraw  # <-- 
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
                            purchase_unit=purchase_nav,
                            remaining_credit=remaining_credit,
                            transaction_image=transaction_image,
                            description=description  # <-- Save description
                        )

                        # 1. Retrieve the latest TotalCapitalRecord (or create one if none exists)
                        latest_capital = TotalCapitalRecord.objects.order_by('-date_time').first()
                        if not latest_capital:
                            # If no record exists, initialize with zeros
                            latest_capital = TotalCapitalRecord.objects.create(
                                total_capital=0,
                                invested_capital=0,
                                available_capital=0,
                                total_circulating_unit=0
                            )

                        # 2. Update available_capital based on transaction type
                        if action_type == 'deposit':
                            new_available_capital = latest_capital.available_capital + amount
                            new_total_circulating_unit = latest_capital.total_circulating_unit + purchase_nav
                            new_total_capital = latest_capital.total_capital + amount
                        elif action_type == 'withdrawal':
                            new_available_capital = latest_capital.available_capital - amount
                            new_total_circulating_unit = latest_capital.total_circulating_unit + purchase_nav  # purchase_nav is negative for withdrawal
                            new_total_capital = latest_capital.total_capital - amount

                        # 3. Optionally, update total_capital and invested_capital as needed
                        # For example, you might want to keep total_capital unchanged, or update it as per your business logic

                        # 4. Create a new TotalCapitalRecord with updated values
                        TotalCapitalRecord.objects.create(
                            total_capital=new_total_capital,  # or update as needed
                            invested_capital=latest_capital.invested_capital,  # or update as needed
                            available_capital=new_available_capital,
                            total_circulating_unit=new_total_circulating_unit
                        )
                    update_nav_record() 
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

@login_required
def user_dashboard(request):
    authorized_user = AuthorizedUser.objects.get(email=request.user.email)
    return render(request, 'mainapp/user_dashboard.html', {
        'authorized_user': authorized_user
    })

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
    total_amount = (total_units * nav) + (user_nav.available_credit_amount if user_nav else 0)
    total_amount_format = indian_number_format(total_amount)
    # Calculate total invested amount (deposits - withdrawals)
    total_deposit = UserTransaction.objects.filter(
        authorized_user__email=request.user.email,
        transaction_type='deposit'
    ).aggregate(total=Sum('purchase_initiated_amount'))['total'] or 0

    total_withdrawal = UserTransaction.objects.filter(
        authorized_user__email=request.user.email,
        transaction_type='withdrawal'
    ).aggregate(total=Sum('purchase_initiated_amount'))['total'] or 0

    total_invested = total_deposit - total_withdrawal
    # Calculate unrealized profit/loss
    available_credit = user_nav.available_credit_amount if user_nav else 0
    unrealized_pl = total_amount - total_invested

    nav_records = NAVRecord.objects.order_by('date_time')
    nav_dates = [nav.date_time.strftime('%Y-%m-%d') for nav in nav_records]
    nav_unit_costs = [float(nav.unit_cost) for nav in nav_records]

    context = {
        'total_units': total_units,
        'nav': nav,
        'nav_date': nav_date,
        'total_amount': total_amount,
        'total_amount_format': total_amount_format,
        'nav_dates_json': json.dumps(nav_dates, cls=DjangoJSONEncoder),
        'nav_unit_costs_json': json.dumps(nav_unit_costs, cls=DjangoJSONEncoder),
        'unrealized_pl': unrealized_pl,
        'total_invested': total_invested,
    }
    return render(request, 'mainapp/portfolio.html', context)

@login_required
def transaction_history(request):
    # Get the authorized user object for the logged-in user
    try:
        authorized_user = AuthorizedUser.objects.get(email=request.user.email)
    except AuthorizedUser.DoesNotExist:
        authorized_user = None

    transactions = []
    if authorized_user:
        transactions = UserTransaction.objects.filter(
            authorized_user=authorized_user
        ).order_by('-date_time')  # Assuming 'date_time' is your transaction date field

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'mainapp/user_transaction_history.html',
            {'transactions': transactions},
            request=request
        )
        return HttpResponse(html)
    return render(
        request,
        'mainapp/user_transaction_history.html',
        {'transactions': transactions}
    )

@login_required
def bank_detail(request):
    user = request.user
    authorized_user = AuthorizedUser.objects.get(email=user.email)
    bank = None
    try:
        bank = authorized_user.bank_detail
    except:
        bank = None

    if request.method == 'POST':
        data = request.POST
        bank_number = data.get('bank_number')
        bank_name = data.get('bank_name')
        account_holder_name = data.get('account_holder_name')
        branch = data.get('branch')
        cell_number = data.get('cell_number')

        bank_obj, created = UserBankDetail.objects.update_or_create(
            authorized_user=authorized_user,
            defaults={
                'bank_number': bank_number,
                'bank_name': bank_name,
                'account_holder_name': account_holder_name,
                'branch': branch,
                'cell_number': cell_number
            }
        )
        return JsonResponse({'success': True, 'message': 'Bank details saved successfully.'})

    html = render_to_string('mainapp/bank_detail_form.html', {'bank': bank}, request=request)
    return JsonResponse({'html': html})

@login_required
def fundmanager_user_portfolio(request):
    email = request.GET.get('email')
    user_obj = get_object_or_404(AuthorizedUser, email=email)

    # Fetch total unit balance for the user
    user_nav = UserNAV.objects.filter(authorized_user=user_obj).first()
    total_units = user_nav.available_unit if user_nav else 0

    # Fetch latest NAV record
    latest_nav_record = NAVRecord.objects.order_by('-date_time').first()
    nav = latest_nav_record.unit_cost if latest_nav_record else 0
    nav_date = latest_nav_record.date_time.strftime('%Y-%m-%d') if latest_nav_record else 'N/A'

    # Calculate total amount
    available_credit = user_nav.available_credit_amount if user_nav else 0
    total_amount = (total_units * nav) + available_credit
    total_amount_display = indian_number_format(total_amount)

    # Calculate total invested amount (deposits - withdrawals)
    total_deposit = UserTransaction.objects.filter(
        authorized_user=user_obj,
        transaction_type='deposit'
    ).aggregate(total=Sum('purchase_initiated_amount'))['total'] or 0

    total_withdrawal = UserTransaction.objects.filter(
        authorized_user=user_obj,
        transaction_type='withdrawal'
    ).aggregate(total=Sum('purchase_initiated_amount'))['total'] or 0

    total_invested = total_deposit - total_withdrawal
    # Calculate unrealized profit/loss
    unrealized_pl = total_amount - total_invested

    nav_records = NAVRecord.objects.order_by('date_time')
    nav_dates = [nav.date_time.strftime('%Y-%m-%d') for nav in nav_records]
    nav_unit_costs = [float(nav.unit_cost) for nav in nav_records]

    context = {
        'user_obj': user_obj,
        'total_units': total_units,
        'nav': nav,
        'nav_date': nav_date,
        'total_amount': total_amount,
        'total_amount_display': total_amount_display,
        'nav_dates_json': json.dumps(nav_dates, cls=DjangoJSONEncoder),
        'nav_unit_costs_json': json.dumps(nav_unit_costs, cls=DjangoJSONEncoder),
        'unrealized_pl': unrealized_pl,
        'total_invested': total_invested,
        'available_credit': available_credit,
    }
    return render(request, 'mainapp/fundmanager_user_portfolio.html', context)

def indian_number_format(amount):
    # Format number as per Indian system (e.g., 10,00,000.00)
    s = f"{amount:,.2f}"
    x = s.split('.')
    if len(x[0]) > 3:
        x[0] = x[0][:-3].replace(',', '')[::-1]
        x[0] = ','.join([x[0][i:i+2] for i in range(0, len(x[0]), 2)])[::-1] + ',' + s[-6:-3]
    return x[0] + '.' + x[1]


def send_transaction_email(user_email, transaction_type, amount, date, balance, transaction_id):
    subject = f"BE Investment Firm: {transaction_type.capitalize()} Notification"
    from_email = "no-reply@beinvestmentfirm.com"
    to_email = [user_email]

    html_content = f"""
    <div style="max-width:520px;margin:0 auto;padding:28px 22px;background:#fffbe6;border-radius:14px;
        border:1.5px solid #bfa14a;font-family:sans-serif;">
        <div style="text-align:center;margin-bottom:18px;">
            <img src="https://yourdomain.com/static/mainapp/assets/be_logo.png" alt="BE Logo" style="width:56px;height:56px;border-radius:10px;">
        </div>
        <h2 style="color:#bfa14a;text-align:center;margin-bottom:10px;">Transaction Alert</h2>
        <p style="color:#14213d;text-align:center;font-size:1.1rem;margin-bottom:18px;">
            Dear Investor,<br>
            Your recent <b>{transaction_type}</b> has been processed successfully.
        </p>
        <div style="background:#fff8e1;border-radius:8px;padding:18px 0;margin:18px 0;text-align:center;">
            <table style="margin:0 auto;font-size:1.05rem;color:#14213d;">
                <tr>
                    <td style="padding:6px 18px;">Transaction ID:</td>
                    <td style="padding:6px 0;font-weight:600;">{transaction_id}</td>
                </tr>
                <tr>
                    <td style="padding:6px 18px;">Type:</td>
                    <td style="padding:6px 0;font-weight:600;">{transaction_type.capitalize()}</td>
                </tr>
                <tr>
                    <td style="padding:6px 18px;">Amount:</td>
                    <td style="padding:6px 0;font-weight:600;">₹ {amount:,.2f}</td>
                </tr>
                <tr>
                    <td style="padding:6px 18px;">Date:</td>
                    <td style="padding:6px 0;font-weight:600;">{date}</td>
                </tr>
                <tr>
                    <td style="padding:6px 18px;">Balance:</td>
                    <td style="padding:6px 0;font-weight:600;">₹ {balance:,.2f}</td>
                </tr>
            </table>
        </div>
        <ul style="color:#6c757d;font-size:0.98rem;margin-bottom:18px;">
            <li>If you did not authorize this transaction, please contact us immediately.</li>
            <li>Keep this email for your records.</li>
        </ul>
        <div style="text-align:center;color:#888;font-size:0.95rem;">
            Need help? Contact <a href="mailto:beinvestmentfirm@gmail.com" style="color:#bfa14a;">beinvestmentfirm@gmail.com</a>
        </div>
    </div>
    """

    text_content = f"""BE Investment Firm Transaction Alert

Transaction ID: {transaction_id}
Type: {transaction_type.capitalize()}
Amount: ₹ {amount:,.2f}
Date: {date}
Balance: ₹ {balance:,.2f}

If you did not authorize this transaction, please contact us immediately.
beinvestmentfirm@gmail.com
"""

    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)




@login_required
def message(request, msg):
    return render(request, 'mainapp/message.html', {'msg': msg})

@login_required
def user_contract(request):
    return render(request, 'mainapp/user_contract.html')

@login_required
def add_investment_transaction(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        investment_id = request.POST.get('investment')
        amount = request.POST.get('amount')
        amount_type = request.POST.get('amount_type')

        try:
            amount = Decimal(amount)
        except (TypeError, ValueError):
            return JsonResponse({"success": False, "error": "Invalid amount."})

        if investment_id and amount and amount_type:
            try:
                with transaction.atomic():
                    investment = FirmInvestment.objects.get(pk=investment_id)

                    # 1. Fetch latest Total Capital Record by ID
                    latest_record = TotalCapitalRecord.objects.latest('id')
                    total_capital = latest_record.total_capital
                    invested_capital = latest_record.invested_capital
                    available_capital = latest_record.available_capital
                    total_circulating_unit = latest_record.total_circulating_unit

                    if amount_type == 'investment':
                        if amount > available_capital:
                            return JsonResponse({"success": False, "error": "Transaction amount exceeds available capital."})
                        new_invested_capital = invested_capital + amount
                        new_available_capital = available_capital - amount
                    elif amount_type == 'return':
                        total_invested = InvestmentTransaction.objects.filter(
                            investment=investment, amount_type='investment'
                        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

                        total_return_before = InvestmentTransaction.objects.filter(
                            investment=investment, amount_type='return'
                        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

                        print("Total Invested:", total_invested)
                        print("Total Return Before:", total_return_before)
                        print("New Return Amount:", amount)
                        if total_invested > (total_return_before + amount):
                            new_available_capital = available_capital + amount
                            new_invested_capital = invested_capital - amount
                        else:
                            remaining_inv = total_invested - total_return_before
                            new_available_capital = available_capital + amount
                            new_invested_capital = invested_capital - remaining_inv
                    else:
                        return JsonResponse({"success": False, "error": "Invalid amount type."})
                    
                    transaction_obj = InvestmentTransaction.objects.create(
                        investment=investment,
                        amount=amount,
                        amount_type=amount_type
                    )

                    # 3. Add another Total Capital Record entry
                    TotalCapitalRecord.objects.create(
                        total_capital=new_invested_capital + new_available_capital,
                        invested_capital=new_invested_capital,
                        available_capital=new_available_capital,
                        total_circulating_unit=total_circulating_unit
                    )
                update_nav_record()
                return JsonResponse({
                    "success": True,
                    "investment": investment.investment_name,
                    "amount": transaction_obj.amount,
                    "amount_type": transaction_obj.get_amount_type_display()
                })
            except FirmInvestment.DoesNotExist:
                return JsonResponse({"success": False, "error": "Selected investment does not exist."})
            except TotalCapitalRecord.DoesNotExist:
                return JsonResponse({"success": False, "error": "No Total Capital Record found."})
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)})
        else:
            return JsonResponse({"success": False, "error": "All fields are required."})

    investments = FirmInvestment.objects.filter(status='open')
    html = render_to_string('mainapp/add_investment_transaction.html', {'investments': investments}, request=request)
    return HttpResponse(html)

from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from .models import FirmInvestment, InvestmentCategory

@login_required
def add_investment_modal(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        investment_name = request.POST.get('investment_name')
        investment_category_id = request.POST.get('investment_category')
        status = request.POST.get('status')
        if investment_name and investment_category_id and status:
            # Check for duplicate investment name
            if FirmInvestment.objects.filter(investment_name=investment_name).exists():
                return JsonResponse({"success": False, "error": "The Investment name already exists - Choose another name"})
            try:
                category = InvestmentCategory.objects.get(pk=investment_category_id)
                investment = FirmInvestment.objects.create(
                    investment_name=investment_name,
                    investment_category=category,
                    status=status
                )
                return JsonResponse({"success": True})
            except InvestmentCategory.DoesNotExist:
                return JsonResponse({"success": False, "error": "Selected category does not exist."})
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)})
        else:
            return JsonResponse({"success": False, "error": "All fields are required."})

    categories = InvestmentCategory.objects.all()
    html = render_to_string('mainapp/add_investment_modal.html', {'categories': categories}, request=request)
    return HttpResponse(html)

@login_required
def close_investment_modal(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        investment_id = request.POST.get('investment_id')
        status = request.POST.get('status')
        if investment_id and status == 'closed':
            try:
                with transaction.atomic():
                    investment = FirmInvestment.objects.get(pk=investment_id, status='open')

                    transactions = InvestmentTransaction.objects.filter(investment=investment)
                    latest_record = TotalCapitalRecord.objects.latest('id')
                    total_capital = latest_record.total_capital
                    invested_capital = latest_record.invested_capital
                    available_capital = latest_record.available_capital
                    total_circulating_unit = latest_record.total_circulating_unit

                    invested_amount = transactions.filter(amount_type='investment').aggregate(total=Sum('amount'))['total'] or Decimal('0')
                    return_amount = transactions.filter(amount_type='return').aggregate(total=Sum('amount'))['total'] or Decimal('0')
                    profit = return_amount - invested_amount

                    if profit > 0:
                        profit_20 = profit * Decimal('0.20')

                        # Fetch latest NAVRecord by id
                        latest_nav = NAVRecord.objects.latest('id')
                        unit_cost = latest_nav.unit_cost

                        # Calculate purchase_unit and remaining_credit
                        purchase_unit = profit_20 // unit_cost
                        remaining_credit = profit_20 - (purchase_unit * unit_cost)

                        be_user = AuthorizedUser.objects.get(email='beinvestmentfirm@gmail.com')
                        UserTransaction.objects.create(
                            authorized_user=be_user,
                            transaction_type='deposit',
                            unit_cost=unit_cost,
                            purchase_initiated_amount=profit_20,
                            purchase_unit=purchase_unit,
                            remaining_credit=remaining_credit,
                            description=f"{investment.investment_name} - profit credited"
                        )

                        # --- Update UserNav for beinvestmentfirm@gmail.com ---
                        user_nav = UserNAV.objects.get(authorized_user=be_user)
                        user_nav.available_unit += purchase_unit
                        user_nav.available_credit_amount += remaining_credit
                        user_nav.save()
                        # -----------------------------------------------------

                        new_available_capital = available_capital
                        TotalCapitalRecord.objects.create(
                            total_capital=invested_capital + new_available_capital,
                            invested_capital=invested_capital,
                            available_capital=new_available_capital,
                            total_circulating_unit=total_circulating_unit + purchase_unit
                        )

                    investment.status = 'closed'
                    investment.save()

                update_nav_record()
                return JsonResponse({"success": True})
            except FirmInvestment.DoesNotExist:
                return JsonResponse({"success": False, "error": "Selected investment does not exist or is already closed."})
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)})
        else:
            return JsonResponse({"success": False, "error": "All fields are required."})

    investments = FirmInvestment.objects.filter(status='open')
    html = render_to_string('mainapp/close_investment_modal.html', {'investments': investments}, request=request)
    return HttpResponse(html)


def upload_transaction(request):
    print("Inside upload_transaction view")
    if request.method == 'POST':
        email = request.user.email if request.user.is_authenticated else request.POST.get('email')
        transaction_file = request.FILES.get('transaction_file')
        amount = request.POST.get('amount')
        description = request.POST.get('description', '')

        if not (email and transaction_file and amount):
            return JsonResponse({'success': False, 'error': 'All fields are required.'})

        try:
            obj, created = UserTransactionUpload.objects.update_or_create(
                email=email,
                defaults={
                    'transaction_file': transaction_file,
                    'amount': amount,
                    'description': description,
                    'date_time': timezone.now()
                }
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})


@login_required
def pending_user_uploads(request):
    # Only allow fund managers
    authorized_user = AuthorizedUser.objects.get(email=request.user.email)
    if authorized_user.role != 'fund_manager':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    uploads = UserTransactionUpload.objects.filter(is_credited=False, is_valid=True).order_by('date_time')
    html = render_to_string('mainapp/pending_user_uploads.html', {'uploads': uploads}, request=request)
    return JsonResponse({'html': html})

@login_required
def edit_user_upload(request, email):
    authorized_user = AuthorizedUser.objects.get(email=request.user.email)
    if authorized_user.role != 'fund_manager':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    upload = get_object_or_404(UserTransactionUpload, email=email)
    if request.method == 'POST':
        is_valid = request.POST.get('is_valid') == 'true'
        is_credited = request.POST.get('is_credited') == 'true'
        upload.is_valid = is_valid
        upload.is_credited = is_credited
        upload.save()
        return JsonResponse({'success': True})

    html = render_to_string('mainapp/edit_user_upload_modal.html', {'upload': upload}, request=request)
    return JsonResponse({'html': html})

from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["GET", "POST"])
def payment_detail(request):
    user = AuthorizedUser.objects.get(email=request.user.email)
    obj, created = UserRecurringPayment.objects.get_or_create(
        authorized_user=user,
        defaults={
            'recurring_payment_amount': 0,
            'payment_date': None
        }
    )
    if request.method == 'GET':
        return JsonResponse({
            'recurring_payment_amount': str(obj.recurring_payment_amount) if obj.recurring_payment_amount else '',
            'payment_date': obj.payment_date.isoformat() if obj.payment_date else ''
        })
    else:
        amount = request.POST.get('recurring_payment_amount')
        date = request.POST.get('payment_date')
        try:
            obj.recurring_payment_amount = amount
            obj.payment_date = date
            obj.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
@login_required
@require_GET
def firm_status_dashboard(request):
    latest_record = TotalCapitalRecord.objects.order_by('-id').first()
    history = TotalCapitalRecord.objects.order_by('date_time').values('date_time', 'total_capital')
    html = render_to_string('mainapp/firm_status_dashboard.html', {
        'latest_record': latest_record,
        'history': list(history),
    })
    return JsonResponse({'html': html})