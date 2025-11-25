from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_GET
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.db.models import Max, Sum
from django.utils import timezone
from .models import AuthorizedUser, UserRecurringPayment, UserTransaction, UserNAV, NAVRecord, UserBankDetail, InvestmentCategory, FirmInvestment, TotalCapitalRecord, InvestmentTransaction, UserTransactionUpload, WithdrawalRequest
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
import sys

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
    code = random.randint(100000, 999999)
    request.session['verification_code'] = str(code)
    request.session['verification_email'] = request.user.email

    subject = 'Your BE Investment Firm Verification Code'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [request.user.email]

    # HTML content
    html_content = f"""
    <div style="max-width:520px;margin:0 auto;padding:32px 24px;background:#ffffff;border-radius:16px;
        box-shadow:0 10px 25px rgba(37,99,235,0.08), 0 4px 12px rgba(37,99,235,0.05);
        border:1px solid rgba(37,99,235,0.1);font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
        <div style="text-align:center;margin-bottom:24px;">
            <div style="width:80px;height:80px;margin:0 auto;background:linear-gradient(135deg,#f8fafc,#f1f5f9);
                border-radius:16px;display:flex;align-items:center;justify-content:center;
                box-shadow:0 4px 12px rgba(37,99,235,0.15);">
                <div style="width:48px;height:48px;background:#2563eb;border-radius:12px;"></div>
            </div>
        </div>
        <h2 style="color:#2563eb;text-align:center;margin-bottom:12px;font-weight:700;font-size:1.75rem;">Email Verification</h2>
        <p style="color:#64748b;text-align:center;font-size:1.1rem;margin-bottom:24px;line-height:1.5;">
            Welcome to <b style="color:#1e293b;">BE Investment Firm</b>!<br>
            Please use the verification code below to complete your registration.
        </p>
        <div style="background:linear-gradient(135deg,#f8fafc,#f1f5f9);border-radius:12px;padding:24px;
            margin:24px 0;text-align:center;border:2px solid rgba(37,99,235,0.1);">
            <span style="font-size:2.2rem;letter-spacing:8px;color:#2563eb;font-weight:700;font-family:monospace;">{code}</span>
        </div>
        <div style="background:#fef3c7;border-radius:8px;padding:16px;margin:20px 0;border-left:4px solid #f59e0b;">
            <ul style="color:#1e293b;font-size:0.95rem;margin:0;padding-left:20px;">
                <li>This code is valid for 10 minutes only</li>
                <li>Do not share your code with anyone</li>
                <li>If you did not request this, please ignore this email</li>
            </ul>
        </div>
        <div style="text-align:center;color:#64748b;font-size:0.95rem;margin-top:24px;">
            Need help? Contact <a href="mailto:beinvestmentfirm@gmail.com" 
                style="color:#2563eb;text-decoration:none;font-weight:500;">beinvestmentfirm@gmail.com</a>
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
        <div style="max-width:520px;margin:0 auto;padding:32px 24px;background:#ffffff;border-radius:16px;
            box-shadow:0 10px 25px rgba(37,99,235,0.08), 0 4px 12px rgba(37,99,235,0.05);
            border:1px solid rgba(37,99,235,0.1);font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
            <div style="text-align:center;margin-bottom:24px;">
                <div style="width:80px;height:80px;margin:0 auto;background:linear-gradient(135deg,#f8fafc,#f1f5f9);
                    border-radius:16px;display:flex;align-items:center;justify-content:center;
                    box-shadow:0 4px 12px rgba(37,99,235,0.15);">
                    <div style="width:48px;height:48px;background:#2563eb;border-radius:12px;"></div>
                </div>
            </div>
            <h2 style="color:#2563eb;text-align:center;margin-bottom:12px;font-weight:700;font-size:1.75rem;">Email Verification</h2>
            <p style="color:#64748b;text-align:center;font-size:1.1rem;margin-bottom:24px;line-height:1.5;">
                Welcome to <b style="color:#1e293b;">BE Investment Firm</b>!<br>
                Please use the verification code below to complete your registration.
            </p>
            <div style="background:linear-gradient(135deg,#f8fafc,#f1f5f9);border-radius:12px;padding:24px;
                margin:24px 0;text-align:center;border:2px solid rgba(37,99,235,0.1);">
                <span style="font-size:2.2rem;letter-spacing:8px;color:#2563eb;font-weight:700;font-family:monospace;">{code}</span>
            </div>
            <div style="background:#fef3c7;border-radius:8px;padding:16px;margin:20px 0;border-left:4px solid #f59e0b;">
                <ul style="color:#1e293b;font-size:0.95rem;margin:0;padding-left:20px;">
                    <li>This code is valid for 10 minutes only</li>
                    <li>Do not share your code with anyone</li>
                    <li>If you did not request this, please ignore this email</li>
                </ul>
            </div>
            <div style="text-align:center;color:#64748b;font-size:0.95rem;margin-top:24px;">
                Need help? Contact <a href="mailto:beinvestmentfirm@gmail.com" 
                    style="color:#2563eb;text-decoration:none;font-weight:500;">beinvestmentfirm@gmail.com</a>
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
                with transaction.atomic():                  # Need to perform transaction inconsistency problem
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
    
    # Fetch portfolio data for dashboard cards
    user_nav = UserNAV.objects.filter(authorized_user__email=request.user.email).first()
    total_units = user_nav.available_unit if user_nav else 0
    
    # Fetch latest NAV record
    latest_nav_record = NAVRecord.objects.order_by('-date_time').first()
    nav = latest_nav_record.unit_cost if latest_nav_record else 0
    nav_date = latest_nav_record.date_time.strftime('%B %d, %Y') if latest_nav_record else 'N/A'
    
    # Calculate total amount (Portfolio Value)
    total_amount = (total_units * nav) + (user_nav.available_credit_amount if user_nav else 0)
    total_amount_format = indian_number_format(total_amount)
    
    # Calculate total invested amount
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
    unrealized_pl = total_amount - total_invested
    
    # Calculate unrealized profit/loss percentage
    if total_invested > 0:
        unrealized_pl_percentage = (unrealized_pl / total_invested) * 100
    else:
        unrealized_pl_percentage = 0
    
    # Fetch NAV data for chart
    nav_records = NAVRecord.objects.order_by('date_time')
    nav_dates = [nav.date_time.strftime('%Y-%m-%d') for nav in nav_records]
    nav_unit_costs = [float(nav.unit_cost) for nav in nav_records]
    
    return render(request, 'mainapp/user_dashboard.html', {
        'authorized_user': authorized_user,
        'portfolio_value': total_amount,
        'portfolio_value_format': total_amount_format,
        'current_nav': nav,
        'nav_date': nav_date,
        'total_units': total_units,
        'unrealized_pl': unrealized_pl,
        'unrealized_pl_percentage': unrealized_pl_percentage,
        'nav_dates_json': json.dumps(nav_dates, cls=DjangoJSONEncoder),
        'nav_unit_costs_json': json.dumps(nav_unit_costs, cls=DjangoJSONEncoder),
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
    
    # Calculate unrealized profit/loss percentage
    if total_invested > 0:
        unrealized_pl_percentage = (unrealized_pl / total_invested) * 100
    else:
        unrealized_pl_percentage = 0

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
        'unrealized_pl_percentage': unrealized_pl_percentage,
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
def investment_history(request):
    """Display all closed investments with profit/loss percentages"""
    try:
        authorized_user = AuthorizedUser.objects.get(email=request.user.email)
    except AuthorizedUser.DoesNotExist:
        return render(request, 'mainapp/investment_history.html', {'error': 'User not found', 'investments': []})

    # Get all closed investments
    closed_investments = FirmInvestment.objects.filter(status='closed').prefetch_related('transactions')
    
    investment_data = []
    profitable_count = 0
    loss_count = 0
    
    for investment in closed_investments:
        # Calculate total invested and total returned
        total_invested = investment.transactions.filter(amount_type='investment').aggregate(
            total=Sum('amount'))['total'] or Decimal('0')
        total_returned = investment.transactions.filter(amount_type='return').aggregate(
            total=Sum('amount'))['total'] or Decimal('0')
        
        # Calculate profit/loss
        profit_loss = total_returned - total_invested
        
        # Calculate profit/loss percentage
        if total_invested > 0:
            profit_loss_percentage = (profit_loss / total_invested) * 100
        else:
            profit_loss_percentage = Decimal('0')
        
        is_profit = profit_loss > 0
        
        if is_profit:
            profitable_count += 1
        elif profit_loss < 0:
            loss_count += 1
        
        investment_data.append({
            'investment': investment,
            'total_invested': total_invested,
            'total_returned': total_returned,
            'profit_loss': profit_loss,
            'profit_loss_percentage': profit_loss_percentage,
            'is_profit': is_profit,
        })
    
    # Sort by profit/loss percentage (descending)
    investment_data.sort(key=lambda x: x['profit_loss_percentage'], reverse=True)
    
    # Calculate average return percentage
    if investment_data:
        total_return_percentage = sum(inv['profit_loss_percentage'] for inv in investment_data)
        average_return = total_return_percentage / len(investment_data)
    else:
        average_return = Decimal('0')
    
    context = {
        'investments': investment_data,
        'authorized_user': authorized_user,
        'total_investments': len(investment_data),
        'profitable_count': profitable_count,
        'loss_count': loss_count,
        'average_return': average_return,
    }
    
    return render(request, 'mainapp/investment_history.html', context)

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
    
    # Calculate unrealized profit/loss percentage
    if total_invested > 0:
        unrealized_pl_percentage = (unrealized_pl / total_invested) * 100
    else:
        unrealized_pl_percentage = 0

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
        'unrealized_pl_percentage': unrealized_pl_percentage,
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
    <div style="max-width:560px;margin:0 auto;padding:32px 24px;background:#ffffff;border-radius:16px;
        box-shadow:0 10px 25px rgba(37,99,235,0.08), 0 4px 12px rgba(37,99,235,0.05);
        border:1px solid rgba(37,99,235,0.1);font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
        <div style="text-align:center;margin-bottom:24px;">
            <div style="width:80px;height:80px;margin:0 auto;background:linear-gradient(135deg,#f8fafc,#f1f5f9);
                border-radius:16px;display:flex;align-items:center;justify-content:center;
                box-shadow:0 4px 12px rgba(37,99,235,0.15);">
                <div style="width:48px;height:48px;background:#2563eb;border-radius:12px;"></div>
            </div>
        </div>
        <h2 style="color:#2563eb;text-align:center;margin-bottom:12px;font-weight:700;font-size:1.75rem;">Transaction Confirmation</h2>
        <p style="color:#64748b;text-align:center;font-size:1.1rem;margin-bottom:24px;line-height:1.5;">
            Dear Investor,<br>
            Your <b style="color:#1e293b;">{transaction_type}</b> transaction has been processed successfully.
        </p>
        <div style="background:linear-gradient(135deg,#f8fafc,#f1f5f9);border-radius:12px;padding:24px;
            margin:24px 0;border:2px solid rgba(37,99,235,0.1);">
            <table style="margin:0 auto;font-size:1.05rem;color:#1e293b;width:100%;border-spacing:0;">
                <tr>
                    <td style="padding:8px 16px;font-weight:500;">Transaction ID:</td>
                    <td style="padding:8px 0;font-weight:700;color:#2563eb;">{transaction_id}</td>
                </tr>
                <tr>
                    <td style="padding:8px 16px;font-weight:500;">Type:</td>
                    <td style="padding:8px 0;font-weight:700;">{transaction_type.capitalize()}</td>
                </tr>
                <tr>
                    <td style="padding:8px 16px;font-weight:500;">Amount:</td>
                    <td style="padding:8px 0;font-weight:700;color:#10b981;">NRs. {amount:,.2f}</td>
                </tr>
                <tr>
                    <td style="padding:8px 16px;font-weight:500;">Date:</td>
                    <td style="padding:8px 0;font-weight:700;">{date}</td>
                </tr>
                <tr>
                    <td style="padding:8px 16px;font-weight:500;">New Balance:</td>
                    <td style="padding:8px 0;font-weight:700;color:#2563eb;">NRs. {balance:,.2f}</td>
                </tr>
            </table>
        </div>
        <div style="background:#fef3c7;border-radius:8px;padding:16px;margin:20px 0;border-left:4px solid #f59e0b;">
            <ul style="color:#1e293b;font-size:0.95rem;margin:0;padding-left:20px;">
                <li>If you did not authorize this transaction, please contact us immediately</li>
                <li>Keep this email for your records</li>
                <li>Your account balance reflects this transaction</li>
            </ul>
        </div>
        <div style="text-align:center;color:#64748b;font-size:0.95rem;margin-top:24px;">
            Need help? Contact <a href="mailto:beinvestmentfirm@gmail.com" 
                style="color:#2563eb;text-decoration:none;font-weight:500;">beinvestmentfirm@gmail.com</a>
        </div>
    </div>
    """

    text_content = f"""BE Investment Firm Transaction Alert

Transaction ID: {transaction_id}
Type: {transaction_type.capitalize()}
Amount: NRs. {amount:,.2f}
Date: {date}
Balance: NRs. {balance:,.2f}

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
        stock_units_purchased = request.POST.get('stock_units_purchased', None)

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

                    # Initialize variables for all transaction types
                    purchase_unit = 0
                    new_invested_capital = invested_capital
                    new_available_capital = available_capital

                    if amount_type == 'investment':
                        if amount > available_capital:
                            return JsonResponse({"success": False, "error": "Transaction amount exceeds available capital."})
                        new_invested_capital = invested_capital + amount
                        new_available_capital = available_capital - amount
                    elif amount_type == 'return':
                        # Initialize purchase_unit for all return scenarios
                        purchase_unit = 0
                        
                        total_invested = InvestmentTransaction.objects.filter(
                            investment=investment, amount_type='investment'
                        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

                        total_return_before = InvestmentTransaction.objects.filter(
                            investment=investment, amount_type='return'
                        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

                        # Calculate what the total return will be after this transaction
                        total_return_after = total_return_before + amount

                        if total_return_before > total_invested:
                            # All returns are profit, so 20% of this amount goes to beinvestmentfirm.com
                            profit_20 = amount * Decimal('0.20')

                            # Fetch latest NAVRecord by id
                            latest_nav = NAVRecord.objects.latest('id')
                            unit_cost = latest_nav.unit_cost
                            
                            be_user = AuthorizedUser.objects.get(email='beinvestmentfirm@gmail.com')
                            be_user_nav = UserNAV.objects.get(authorized_user=be_user)

                            profit_20 = profit_20 + be_user_nav.available_credit_amount
                            # Calculate purchase units and remaining credit

                            purchase_unit = profit_20 // unit_cost
                            remaining_credit = profit_20 - (purchase_unit * unit_cost)

                            UserTransaction.objects.create(
                                authorized_user=be_user,
                                transaction_type='deposit',
                                unit_cost=unit_cost,
                                purchase_initiated_amount=profit_20,
                                purchase_unit=purchase_unit,
                                remaining_credit=remaining_credit,
                                description=f"{investment.investment_name} - profit credited"
                            )

                            # Update UserNav for beinvestmentfirm@gmail.com
                            user_nav = UserNAV.objects.get(authorized_user=be_user)
                            user_nav.available_unit += purchase_unit
                            user_nav.available_credit_amount = remaining_credit
                            user_nav.save()

                            new_available_capital = available_capital + amount
                            new_invested_capital = invested_capital

                        else:
                            # Only the profit portion above total_invested is subject to 20%
                            profit = total_return_after - total_invested
                            if profit > 0:
                                profit_20 = profit * Decimal('0.20')

                                latest_nav = NAVRecord.objects.latest('id')
                                unit_cost = latest_nav.unit_cost

                                be_user = AuthorizedUser.objects.get(email='beinvestmentfirm@gmail.com')
                                be_user_nav = UserNAV.objects.get(authorized_user=be_user)
                                
                                profit_20 = profit_20 + be_user_nav.available_credit_amount

                                purchase_unit = profit_20 // unit_cost
                                remaining_credit = profit_20 - (purchase_unit * unit_cost)

                                UserTransaction.objects.create(
                                    authorized_user=be_user,
                                    transaction_type='deposit',
                                    unit_cost=unit_cost,
                                    purchase_initiated_amount=profit_20,
                                    purchase_unit=purchase_unit,
                                    remaining_credit=remaining_credit,
                                    description=f"{investment.investment_name} - profit credited"
                                )

                                # Update UserNav for beinvestmentfirm@gmail.com
                                user_nav = UserNAV.objects.get(authorized_user=be_user)
                                user_nav.available_unit += purchase_unit
                                user_nav.available_credit_amount = remaining_credit
                                user_nav.save()

                            new_available_capital = available_capital + amount
                            new_invested_capital = invested_capital - (amount - profit) if profit > 0 else invested_capital - amount
                        
                        total_circulating_unit += purchase_unit
                    else:
                        return JsonResponse({"success": False, "error": "Invalid amount type."})
                    
                    transaction_obj = InvestmentTransaction.objects.create(
                        investment=investment,
                        amount=amount,
                        amount_type=amount_type,
                        stock_units_purchased=stock_units_purchased if stock_units_purchased else None
                    )

                    # 3. Add another Total Capital Record entry
                    TotalCapitalRecord.objects.create(
                        total_capital=new_invested_capital + new_available_capital,
                        invested_capital=new_invested_capital,
                        available_capital=new_available_capital,
                        total_circulating_unit=total_circulating_unit
                    )
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
        share_symbol = request.POST.get('share_symbol', '').strip()
        
        if investment_name and investment_category_id and status:
            # Check for duplicate investment name
            if FirmInvestment.objects.filter(investment_name=investment_name).exists():
                return JsonResponse({"success": False, "error": "The Investment name already exists - Choose another name"})
            try:
                category = InvestmentCategory.objects.get(pk=investment_category_id)
                
                # If share market category is selected, share_symbol should be provided
                if category.category_name.lower() == 'share market' and not share_symbol:
                    return JsonResponse({"success": False, "error": "Share symbol is required for share market investments."})
                
                investment = FirmInvestment.objects.create(
                    investment_name=investment_name,
                    investment_category=category,
                    status=status,
                    share_symbol=share_symbol if share_symbol else None
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

                    # Check if this is a share market investment and validate remaining units
                    if (investment.investment_category and 
                        investment.investment_category.category_name.lower() == 'share market' and 
                        investment.share_symbol):
                        
                        # Get all transactions for this investment
                        investment_transactions = InvestmentTransaction.objects.filter(investment=investment)
                        
                        # Calculate total stock units purchased
                        total_units_purchased = investment_transactions.filter(
                            amount_type='investment',
                            stock_units_purchased__isnull=False
                        ).aggregate(total=Sum('stock_units_purchased'))['total'] or Decimal('0')
                        
                        # Calculate total stock units sold (returned)
                        total_units_sold = investment_transactions.filter(
                            amount_type='return',
                            stock_units_purchased__isnull=False
                        ).aggregate(total=Sum('stock_units_purchased'))['total'] or Decimal('0')
                        
                        # Calculate remaining units
                        remaining_units = total_units_purchased - total_units_sold
                        
                        if remaining_units > 0:
                            return JsonResponse({
                                "success": False, 
                                "error": f"Cannot close share market investment '{investment.investment_name}' ({investment.share_symbol}). "
                                        f"There are {remaining_units} units remaining. Please sell all shares before closing the investment."
                            })

                    transactions = InvestmentTransaction.objects.filter(investment=investment)
                    latest_record = TotalCapitalRecord.objects.latest('id')
                    total_capital = latest_record.total_capital
                    invested_capital = latest_record.invested_capital
                    available_capital = latest_record.available_capital
                    total_circulating_unit = latest_record.total_circulating_unit

                    # Calculate profit/loss for the investment
                    invested_amount = transactions.filter(amount_type='investment').aggregate(total=Sum('amount'))['total'] or Decimal('0')
                    return_amount = transactions.filter(amount_type='return').aggregate(total=Sum('amount'))['total'] or Decimal('0')
                    profit_loss = return_amount - invested_amount
                    
                    # If investment is in loss, subtract the loss from invested capital
                    if profit_loss < 0:
                        loss_amount = abs(profit_loss)  # Make it positive
                        new_invested_capital = invested_capital - loss_amount
                        new_total_capital = new_invested_capital + available_capital
                        
                        # Create new TotalCapitalRecord to reflect the loss
                        TotalCapitalRecord.objects.create(
                            total_capital=new_total_capital,
                            invested_capital=new_invested_capital,
                            available_capital=available_capital,
                            total_circulating_unit=total_circulating_unit
                        )

                    # Close the investment
                    investment.status = 'closed'
                    investment.save()

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
            # Create a new upload record every time
            obj = UserTransactionUpload.objects.create(
                email=email,
                transaction_file=transaction_file,
                amount=amount,
                description=description,
                is_valid=True,
                is_credited=False
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
def edit_user_upload(request, upload_id):
    authorized_user = AuthorizedUser.objects.get(email=request.user.email)
    if authorized_user.role != 'fund_manager':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    upload = get_object_or_404(UserTransactionUpload, id=upload_id)
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

@login_required
def withdraw_request(request):
    """
    Handle withdrawal request workflow:
    1. Check if user has bank details
    2. If not, prompt to fill bank details first
    3. If yes, show withdrawal request form
    4. Validate withdrawal amount against available balance
    """
    print(f"DEBUG - withdraw_request called with method: {request.method}")
    
    try:
        authorized_user = AuthorizedUser.objects.get(email=request.user.email)
        print(f"DEBUG - Found authorized user: {authorized_user.email}")
    except AuthorizedUser.DoesNotExist:
        print("DEBUG - AuthorizedUser.DoesNotExist")
        return JsonResponse({'error': 'User not authorized'}, status=403)
    
    if request.method == 'GET':
        print("DEBUG - Processing GET request")
        # Check if user has bank details
        try:
            bank_detail = UserBankDetail.objects.get(authorized_user=authorized_user)
            print(f"DEBUG - Found bank details for user")
        except UserBankDetail.DoesNotExist:
            print("DEBUG - No bank details found")
            bank_detail = None
        
        if not bank_detail:
            # User needs to fill bank details first
            html = render_to_string('mainapp/withdraw_request_no_bank.html', {
                'authorized_user': authorized_user,
            })
            return JsonResponse({'html': html})
        
        print("DEBUG - User has bank details, preparing withdrawal form")
        # User has bank details, show withdrawal form
        # Get user's available balance for validation
        user_nav = None
        latest_nav = None
        total_available = Decimal('0.00')
        
        try:
            user_nav = UserNAV.objects.get(authorized_user=authorized_user)
            print(f"DEBUG - Found UserNAV: units={user_nav.available_unit}, credit={user_nav.available_credit_amount}")
            latest_nav = NAVRecord.objects.latest('id')
            print(f"DEBUG - Latest NAV: {latest_nav.unit_cost}")
            
            # Calculate available balance: (units * current_nav) + credit
            available_portfolio_value = user_nav.available_unit * latest_nav.unit_cost
            total_available = available_portfolio_value + user_nav.available_credit_amount
            print(f"DEBUG - Calculated total_available: {total_available}")
            
        except (UserNAV.DoesNotExist, NAVRecord.DoesNotExist) as e:
            print(f"DEBUG - Exception getting NAV data: {e}")
            total_available = Decimal('0.00')
        
        # Calculate portfolio value for display
        available_units = user_nav.available_unit if user_nav else Decimal('0.00')
        available_credit = user_nav.available_credit_amount if user_nav else Decimal('0.00')
        current_nav = latest_nav.unit_cost if latest_nav else Decimal('0.00')
        portfolio_value = available_units * current_nav
        
        # Add CSRF token to context
        from django.middleware.csrf import get_token
        html = render_to_string('mainapp/withdraw_request_form.html', {
            'authorized_user': authorized_user,
            'bank_detail': bank_detail,
            'total_available': total_available,
            'available_units': available_units,
            'available_credit': available_credit,
            'current_nav': current_nav,
            'portfolio_value': portfolio_value,
            'csrf_token': get_token(request),
        }, request=request)
        return JsonResponse({'html': html})
    
    elif request.method == 'POST':
        # Process withdrawal request submission
        from .models import WithdrawalRequest
        
        # Validate that user has bank details
        try:
            bank_detail = UserBankDetail.objects.get(authorized_user=authorized_user)
        except UserBankDetail.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Please set up your bank details first.'
            })
        
        # Get form data
        requested_amount = request.POST.get('requested_amount')
        withdrawal_type = request.POST.get('withdrawal_type', 'partial')
        user_reason = request.POST.get('user_reason', '')
        
        try:
            requested_amount = Decimal(requested_amount)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid withdrawal amount.'
            })
        
        # Validate withdrawal amount
        try:
            user_nav = UserNAV.objects.get(authorized_user=authorized_user)
            latest_nav = NAVRecord.objects.latest('id')
            
            # Calculate available balance
            available_portfolio_value = user_nav.available_unit * latest_nav.unit_cost
            total_available = available_portfolio_value + user_nav.available_credit_amount
            
            if requested_amount > total_available:
                return JsonResponse({
                    'success': False,
                    'error': f'Requested amount (NRs. {requested_amount}) exceeds available balance (NRs. {total_available}).'
                })
            
            # Create withdrawal request
            withdrawal_request = WithdrawalRequest.objects.create(
                authorized_user=authorized_user,
                requested_amount=requested_amount,
                withdrawal_type=withdrawal_type,
                bank_detail=bank_detail,
                user_reason=user_reason,
                available_balance_at_request=total_available,
                available_units_at_request=user_nav.available_unit,
                current_nav_at_request=latest_nav.unit_cost,
                created_from_ip=get_client_ip(request)
            )
            
            return JsonResponse({
                'success': True,
                'withdrawal_id': withdrawal_request.withdrawal_id,
                'requested_amount': str(requested_amount),
                'message': 'Withdrawal request submitted successfully!'
            })
            
        except (UserNAV.DoesNotExist, NAVRecord.DoesNotExist) as e:
            return JsonResponse({
                'success': False,
                'error': 'Unable to process withdrawal request. Please contact support.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            })

def get_client_ip(request):
    """Get client's IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def fundmanager_withdrawal_requests(request):
    """Fund manager view for managing withdrawal requests"""
    try:
        authorized_user = AuthorizedUser.objects.get(email=request.user.email)
        if authorized_user.role != 'fund_manager':
            return redirect('home')
    except AuthorizedUser.DoesNotExist:
        return redirect('home')
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    priority_filter = request.GET.get('priority', 'all')
    
    # Base query
    withdrawal_requests = WithdrawalRequest.objects.select_related('authorized_user', 'bank_detail').all()
    
    # Apply filters
    if status_filter != 'all':
        withdrawal_requests = withdrawal_requests.filter(status=status_filter)
    if priority_filter != 'all':
        withdrawal_requests = withdrawal_requests.filter(priority=priority_filter)
    
    # Get status choices for filter dropdown
    status_choices = WithdrawalRequest.STATUS_CHOICES
    priority_choices = WithdrawalRequest.PRIORITY_CHOICES
    
    context = {
        'withdrawal_requests': withdrawal_requests,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': status_choices,
        'priority_choices': priority_choices,
    }
    
    return render(request, 'mainapp/fundmanager_withdrawal_requests.html', context)

@login_required
def fundmanager_withdrawal_detail(request, withdrawal_id):
    """Fund manager detailed view for a specific withdrawal request"""
    print("="*50, file=sys.stderr, flush=True)
    print(f"FUNDMANAGER_WITHDRAWAL_DETAIL CALLED! withdrawal_id={withdrawal_id}", file=sys.stderr, flush=True)
    print("="*50, file=sys.stderr, flush=True)
    
    # Also print to regular stdout
    print("="*50)
    print(f"FUNDMANAGER_WITHDRAWAL_DETAIL CALLED! withdrawal_id={withdrawal_id}")
    print("="*50)
    
    try:
        authorized_user = AuthorizedUser.objects.get(email=request.user.email)
        if authorized_user.role != 'fund_manager':
            return redirect('home')
    except AuthorizedUser.DoesNotExist:
        return redirect('home')
    
    try:
        withdrawal_request = WithdrawalRequest.objects.select_related(
            'authorized_user', 'bank_detail'
        ).get(withdrawal_id=withdrawal_id)
    except WithdrawalRequest.DoesNotExist:
        return redirect('fundmanager_withdrawal_requests')
    
    # Fetch UserNAV for that email (current data)
    user_email = withdrawal_request.authorized_user.email
    

    # Get current UserNAV (real-time data)
    user_nav = UserNAV.objects.filter(authorized_user__email=user_email).first()
    
    # Fetch current NAV records (latest by id)
    try:
        latest_nav_record = NAVRecord.objects.latest('id')
    except NAVRecord.DoesNotExist:
        latest_nav_record = None

    
    # Calculate current values (for Current Financial Detail card)
    available_unit = user_nav.available_unit if user_nav else Decimal('0.00')
    available_credit = user_nav.available_credit_amount if user_nav else Decimal('0.00')
    unit_cost = latest_nav_record.unit_cost if latest_nav_record else Decimal('0.00')
    portfolio_value = available_unit * unit_cost
    

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('status')
            priority = request.POST.get('priority')
            manager_notes = request.POST.get('manager_notes', '')
            approved_amount = request.POST.get('approved_amount')
            rejection_reason = request.POST.get('rejection_reason', '')
            
            # Update withdrawal request
            withdrawal_request.status = new_status
            withdrawal_request.priority = priority
            withdrawal_request.manager_notes = manager_notes
            withdrawal_request.reviewed_by = request.user.email
            withdrawal_request.reviewed_date = timezone.now()
            
            if new_status == 'approved' and approved_amount:
                withdrawal_request.approved_amount = Decimal(approved_amount)
            elif new_status == 'rejected' and rejection_reason:
                withdrawal_request.rejection_reason = rejection_reason
            
            withdrawal_request.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Withdrawal request {new_status} successfully'
            })
        
        elif action == 'process_withdrawal':
            processed_amount = request.POST.get('processed_amount')
            processing_fee = request.POST.get('processing_fee', '0')
            units_redeemed = request.POST.get('units_redeemed')
            
            try:
                with transaction.atomic():
                    # Update withdrawal request
                    withdrawal_request.status = 'processed'
                    withdrawal_request.processed_by = request.user.email
                    withdrawal_request.processed_date = timezone.now()
                    withdrawal_request.actual_processed_amount = Decimal(processed_amount)
                    withdrawal_request.processing_fee = Decimal(processing_fee)
                    withdrawal_request.units_redeemed = Decimal(units_redeemed) if units_redeemed else None
                    withdrawal_request.save()
                    
                    # Update user's NAV if units were redeemed
                    if units_redeemed:
                        user_nav = UserNAV.objects.get(authorized_user=withdrawal_request.authorized_user)
                        user_nav.available_unit -= Decimal(units_redeemed)
                        user_nav.save()
                    
                    return JsonResponse({
                        'success': True, 
                        'message': 'Withdrawal processed successfully'
                    })
                    
            except Exception as e:
                return JsonResponse({
                    'success': False, 
                    'error': f'Error processing withdrawal: {str(e)}'
                })
    
    context = {
        'withdrawal_request': withdrawal_request,
        'status_choices': WithdrawalRequest.STATUS_CHOICES,
        'priority_choices': WithdrawalRequest.PRIORITY_CHOICES,
        'user_nav': user_nav,
        'available_unit': available_unit,
        'available_credit': available_credit,
        'unit_cost': unit_cost,
        'portfolio_value': portfolio_value,
    }
    
    return render(request, 'mainapp/fundmanager_withdrawal_detail.html', context)

@login_required
def stock_performance_dashboard(request):
    """Display stock performance dashboard showing profit/loss for share market investments."""
    import csv
    import os
    
    # Get all open share market investments
    share_market_category = InvestmentCategory.objects.filter(category_name__icontains='share market').first()
    if not share_market_category:
        return render(request, 'mainapp/stock_performance_dashboard.html', {
            'error': 'Share Market investment category not found.'
        })
    
    share_investments = FirmInvestment.objects.filter(
        investment_category=share_market_category,
        status='open',
        share_symbol__isnull=False
    ).exclude(share_symbol='')
    
    # Load share price data from CSV
    csv_path = os.path.join(settings.BASE_DIR, 'mainapp', 'utilities', 'share_price.csv')
    share_prices = {}
    
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                symbol = row['Symbol'].strip()
                ltp_str = row['LTP'].replace(',', '').strip()
                try:
                    ltp = Decimal(ltp_str)
                    share_prices[symbol] = ltp
                except (ValueError, TypeError):
                    continue
    except FileNotFoundError:
        return render(request, 'mainapp/stock_performance_dashboard.html', {
            'error': 'Share price data file not found.'
        })
    
    # Get latest total capital record
    try:
        latest_capital_record = TotalCapitalRecord.objects.latest('id')
        total_capital = latest_capital_record.total_capital
    except TotalCapitalRecord.DoesNotExist:
        total_capital = Decimal('0')
    
    # Calculate performance for each investment
    investment_performance = []
    total_invested = Decimal('0')
    total_current_value = Decimal('0')
    total_returns = Decimal('0')
    
    for investment in share_investments:
        # Get all transactions for this investment
        investment_transactions = InvestmentTransaction.objects.filter(investment=investment)
        returns_transactions = investment_transactions.filter(amount_type='return')
        
        # Calculate total invested amount
        invested_amount = investment_transactions.filter(amount_type='investment').aggregate(
            total=Sum('amount'))['total'] or Decimal('0')
        
        # Calculate total return amount
        return_amount = returns_transactions.aggregate(
            total=Sum('amount'))['total'] or Decimal('0')
        
        # Calculate total stock units (investment units - return units)
        investment_units = investment_transactions.filter(
            amount_type='investment',
            stock_units_purchased__isnull=False
        ).aggregate(total=Sum('stock_units_purchased'))['total'] or Decimal('0')
        
        return_units = investment_transactions.filter(
            amount_type='return',
            stock_units_purchased__isnull=False
        ).aggregate(total=Sum('stock_units_purchased'))['total'] or Decimal('0')
        
        total_units = investment_units - return_units
        
        # Get current LTP for this share
        current_ltp = share_prices.get(investment.share_symbol, Decimal('0'))
        
        # Calculate current market value
        current_market_value = total_units * current_ltp if current_ltp > 0 else Decimal('0')
        
        # Calculate profit/loss
        net_invested = invested_amount - return_amount
        profit_loss = current_market_value - net_invested
        profit_loss_percentage = (profit_loss / net_invested * 100) if net_invested > 0 else Decimal('0')
        
        # Calculate average buy price (based on investment transactions only)
        avg_buy_price = invested_amount / investment_units if investment_units > 0 else Decimal('0')
        
        # Calculate percentage of total capital invested in this firm
        capital_percentage = (net_invested / total_capital * 100) if total_capital > 0 else Decimal('0')
        
        investment_data = {
            'investment': investment,
            'symbol': investment.share_symbol,
            'invested_amount': invested_amount,
            'return_amount': return_amount,
            'net_invested': net_invested,
            'total_units': total_units,
            'avg_buy_price': avg_buy_price,
            'current_ltp': current_ltp,
            'current_market_value': current_market_value,
            'profit_loss': profit_loss,
            'profit_loss_percentage': profit_loss_percentage,
            'capital_percentage': capital_percentage,
            'transactions': investment_transactions.order_by('-id')
        }
        
        investment_performance.append(investment_data)
        
        # Add to totals
        total_invested += net_invested
        total_current_value += current_market_value
        total_returns += return_amount
    
    # Calculate overall performance
    overall_profit_loss = total_current_value - total_invested
    overall_profit_loss_percentage = (overall_profit_loss / total_invested * 100) if total_invested > 0 else Decimal('0')
    
    context = {
        'investment_performance': investment_performance,
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'total_returns': total_returns,
        'overall_profit_loss': overall_profit_loss,
        'overall_profit_loss_percentage': overall_profit_loss_percentage,
        'total_capital': total_capital,
        'share_market_count': len(investment_performance),
    }
    
    return render(request, 'mainapp/stock_performance_dashboard.html', context)


@login_required
def user_uploads_status(request):
    """View for users to see their transaction uploads and status"""
    try:
        user_email = request.user.email
        uploads = UserTransactionUpload.objects.filter(email=user_email).order_by('-date_time')
        
        # Add status display logic to each upload
        for upload in uploads:
            if upload.is_valid and upload.is_credited:
                upload.status_display = 'Complete'
                upload.status_class = 'success'
            elif upload.is_valid and not upload.is_credited:
                upload.status_display = 'Pending'
                upload.status_class = 'warning'
            else:
                upload.status_display = 'Invalid'
                upload.status_class = 'danger'
        
        context = {
            'uploads': uploads,
            'user_email': user_email,
        }
        
        return render(request, 'mainapp/user_uploads_status.html', context)
        
    except Exception as e:
        context = {
            'error': f'Error retrieving uploads: {str(e)}',
            'uploads': [],
            'user_email': request.user.email,
        }
        return render(request, 'mainapp/user_uploads_status.html', context)

