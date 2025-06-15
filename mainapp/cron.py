from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from .models import UserTransaction, AuthorizedUser

def send_transaction_email(user_email, transactions):
    subject = "BE Investment Firm: Daily Transaction Summary"
    from_email = "no-reply@beinvestmentfirm.com"
    to_email = [user_email]

    rows = ""
    for txn in transactions:
        rows += f"""
        <tr>
            <td style="padding:6px 12px;">{txn.transaction_type.capitalize()}</td>
            <td style="padding:6px 12px;">₹ {txn.purchase_initiated_amount:,.2f}</td>
            <td style="padding:6px 12px;">{txn.date_time.strftime('%Y-%m-%d %H:%M')}</td>
            <td style="padding:6px 12px;">{txn.id}</td>
        </tr>
        """

    html_content = f"""
    <div style="max-width:520px;margin:0 auto;padding:28px 22px;background:#fffbe6;border-radius:14px;
        border:1.5px solid #bfa14a;font-family:sans-serif;">
        <div style="text-align:center;margin-bottom:18px;">
            <img src="https://yourdomain.com/static/mainapp/assets/be_logo.png" alt="BE Logo" style="width:56px;height:56px;border-radius:10px;">
        </div>
        <h2 style="color:#bfa14a;text-align:center;margin-bottom:10px;">Daily Transaction Summary</h2>
        <p style="color:#14213d;text-align:center;font-size:1.1rem;margin-bottom:18px;">
            Dear Investor,<br>
            Here is a summary of your transactions for {timezone.now().date() - timedelta(days=1)}.
        </p>
        <table style="margin:0 auto;font-size:1.05rem;color:#14213d;width:100%;border-collapse:collapse;">
            <thead>
                <tr style="background:#f5e9c6;">
                    <th>Type</th>
                    <th>Amount</th>
                    <th>Date & Time</th>
                    <th>Transaction ID</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        <ul style="color:#6c757d;font-size:0.98rem;margin-bottom:18px;">
            <li>If you did not authorize these transactions, please contact us immediately.</li>
            <li>Keep this email for your records.</li>
        </ul>
        <div style="text-align:center;color:#888;font-size:0.95rem;">
            Need help? Contact <a href="mailto:beinvestmentfirm@gmail.com" style="color:#bfa14a;">beinvestmentfirm@gmail.com</a>
        </div>
    </div>
    """

    text_content = "Your BE Investment Firm transactions for yesterday:\n"
    for txn in transactions:
        text_content += f"{txn.transaction_type.capitalize()} | ₹ {txn.purchase_initiated_amount:,.2f} | {txn.date_time.strftime('%Y-%m-%d %H:%M')} | ID: {txn.id}\n"

    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)

def daily_transaction_email_job():
    # Get yesterday's date range
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    start = datetime.combine(yesterday, datetime.min.time()).replace(tzinfo=timezone.get_current_timezone())
    end = datetime.combine(yesterday, datetime.max.time()).replace(tzinfo=timezone.get_current_timezone())

    # Find all users with transactions yesterday
    user_ids = UserTransaction.objects.filter(date_time__range=(start, end)).values_list('authorized_user', flat=True).distinct()
    for user_id in user_ids:
        user = AuthorizedUser.objects.get(pk=user_id)
        transactions = UserTransaction.objects.filter(authorized_user=user, date_time__range=(start, end))
        send_transaction_email(user.email, transactions)