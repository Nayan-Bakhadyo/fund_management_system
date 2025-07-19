from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from .models import UserTransaction, AuthorizedUser

print("=== daily_transaction_email_job STARTED ===")
def send_transaction_email(user_email, transactions):
    subject = "BE Investment Firm: Transaction Notification"
    from_email = "no-reply@beinvestmentfirm.com"
    to_email = [user_email]

    rows = ""
    for txn in transactions:
        rows += f"""
        <tr style="border-bottom:1px solid rgba(37,99,235,0.1);">
            <td style="padding:12px 8px;font-weight:500;">{txn.transaction_type.capitalize()}</td>
            <td style="padding:12px 8px;font-weight:600;color:#10b981;">NRs. {txn.purchase_initiated_amount:,.2f}</td>
            <td style="padding:12px 8px;">{txn.date_time.strftime('%Y-%m-%d %H:%M')}</td>
            <td style="padding:12px 8px;color:#2563eb;font-weight:500;">{txn.id}</td>
        </tr>
        """

    html_content = f"""
    <div style="max-width:600px;margin:0 auto;padding:32px 24px;background:#ffffff;border-radius:16px;
        box-shadow:0 10px 25px rgba(37,99,235,0.08), 0 4px 12px rgba(37,99,235,0.05);
        border:1px solid rgba(37,99,235,0.1);font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
        <div style="text-align:center;margin-bottom:24px;">
            <div style="width:80px;height:80px;margin:0 auto;background:linear-gradient(135deg,#f8fafc,#f1f5f9);
                border-radius:16px;display:flex;align-items:center;justify-content:center;
                box-shadow:0 4px 12px rgba(37,99,235,0.15);">
                <div style="width:48px;height:48px;background:#2563eb;border-radius:12px;"></div>
            </div>
        </div>
        <h2 style="color:#2563eb;text-align:center;margin-bottom:12px;font-weight:700;font-size:1.75rem;">Transaction Summary</h2>
        <p style="color:#64748b;text-align:center;font-size:1.1rem;margin-bottom:24px;line-height:1.5;">
            Dear Investor,<br>
            Here is a summary of your transactions for <b style="color:#1e293b;">{timezone.now().date() - timedelta(days=1)}</b>.
        </p>
        <div style="background:linear-gradient(135deg,#f8fafc,#f1f5f9);border-radius:12px;padding:20px;
            margin:24px 0;border:2px solid rgba(37,99,235,0.1);overflow-x:auto;">
            <table style="width:100%;font-size:1rem;color:#1e293b;border-collapse:collapse;">
            <table style="width:100%;font-size:1rem;color:#1e293b;border-collapse:collapse;">
                <thead>
                    <tr style="background:linear-gradient(135deg,#2563eb,#3b82f6);color:#ffffff;">
                        <th style="padding:12px 8px;text-align:left;border-radius:8px 0 0 8px;font-weight:600;">Type</th>
                        <th style="padding:12px 8px;text-align:left;font-weight:600;">Amount</th>
                        <th style="padding:12px 8px;text-align:left;font-weight:600;">Date & Time</th>
                        <th style="padding:12px 8px;text-align:left;border-radius:0 8px 8px 0;font-weight:600;">Transaction ID</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        <div style="background:#fef3c7;border-radius:8px;padding:16px;margin:20px 0;border-left:4px solid #f59e0b;">
            <ul style="color:#1e293b;font-size:0.95rem;margin:0;padding-left:20px;">
                <li>If you did not authorize these transactions, please contact us immediately</li>
                <li>Keep this email for your records</li>
                <li>Your account balance reflects these transactions</li>
            </ul>
        </div>
        <div style="text-align:center;color:#64748b;font-size:0.95rem;margin-top:24px;">
            Need help? Contact <a href="mailto:beinvestmentfirm@gmail.com" 
                style="color:#2563eb;text-decoration:none;font-weight:500;">beinvestmentfirm@gmail.com</a>
        </div>
    </div>
    """

    text_content = "Your BE Investment Firm transactions for yesterday:\n"
    for txn in transactions:
        text_content += f"{txn.transaction_type.capitalize()} | NRs. {txn.purchase_initiated_amount:,.2f} | {txn.date_time.strftime('%Y-%m-%d %H:%M')} | ID: {txn.id}\n"

    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)

def daily_transaction_email_job():
    print("daily_transaction_email_job started")
    # Get yesterday's date range
    today = timezone.now().date()
    yesterday = today
    start = datetime.combine(yesterday, datetime.min.time()).replace(tzinfo=timezone.get_current_timezone())
    end = datetime.combine(yesterday, datetime.max.time()).replace(tzinfo=timezone.get_current_timezone())

    # Find all users with transactions yesterday
    user_emails = UserTransaction.objects.filter(date_time__range=(start, end)).values_list('authorized_user', flat=True).distinct()
    print("User IDs/Emails found:", list(user_emails))
    for user_email in user_emails:
        try:
            user = AuthorizedUser.objects.get(email=user_email)
        except AuthorizedUser.DoesNotExist:
            print(f"Skipping invalid user email: {user_email}")
            continue
        transactions = UserTransaction.objects.filter(authorized_user=user_email, date_time__range=(start, end))
        send_transaction_email(user.email, transactions)
