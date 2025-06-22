from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from mainapp.models import UserTransaction, AuthorizedUser  # Adjust import path
import traceback

class Command(BaseCommand):
    help = 'Send daily transaction emails to authorized users'

    def handle(self, *args, **options):
        try:
            today = timezone.now().date()
            yesterday = today
            start = datetime.combine(yesterday, datetime.min.time()).replace(tzinfo=timezone.get_current_timezone())
            end = datetime.combine(yesterday, datetime.max.time()).replace(tzinfo=timezone.get_current_timezone())

            user_emails = UserTransaction.objects.filter(date_time__range=(start, end)).values_list('authorized_user', flat=True).distinct()
            self.stdout.write(f"User IDs/Emails found: {list(user_emails)}")

            for user_email in user_emails:
                try:
                    user = AuthorizedUser.objects.get(email=user_email)
                except AuthorizedUser.DoesNotExist:
                    self.stdout.write(f"Skipping invalid user email: {user_email}")
                    continue
                transactions = UserTransaction.objects.filter(authorized_user=user_email, date_time__range=(start, end))
                self.send_transaction_email(user.email, transactions)

        except Exception as e:
            traceback.print_exc()
            self.stdout.write(self.style.ERROR(f"Error in daily_transaction_email_job: {str(e)}"))

    def send_transaction_email(self, user_email, transactions):
        subject = "BE Investment Firm: Transaction Notification"
        from_email = "no-reply@beinvestmentfirm.com"
        to_email = [user_email]

        rows = ""
        for txn in transactions:
            rows += f"""
            <tr>
                <td style="padding:6px 12px;">{txn.transaction_type.capitalize()}</td>
                <td style="padding:6px 12px;">NRs. {txn.purchase_initiated_amount:,.2f}</td>
                <td style="padding:6px 12px;">{txn.date_time.strftime('%Y-%m-%d %H:%M')}</td>
                <td style="padding:6px 12px;">{txn.id}</td>
            </tr>
            """
        html_content = f"""<div style="max-width:540px;margin:0 auto;padding:32px 18px;background:#e8f9f1;border-radius:18px;border:2px solid #7ed957;font-family:sans-serif;">
            <div style="text-align:center;margin-bottom:22px;">
                <img src="https://beinvestmentfirm.com/static/mainapp/assets/BE_logo_final2.png" alt="BE Logo" style="width:112px;height:80px;border-radius:18px;box-shadow:0 2px 12px #b2f2dd;">
            </div>
            <h2 style="color:#38b000;text-align:center;margin-bottom:12px;">Transaction Summary</h2>
            <p style="color:#1b4332;text-align:center;font-size:1.15rem;margin-bottom:22px;">
                Dear Investor,<br>Here is a summary of your transactions for {timezone.now().date() - timedelta(days=1)}.
            </p>
            <table style="margin:0 auto;font-size:1.08rem;color:#1b4332;width:100%;border-collapse:collapse;">
                <thead><tr style="background:#b2f2dd;"><th>Type</th><th>Amount</th><th>Date & Time</th><th>Transaction ID</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
            <ul style="color:#40916c;font-size:1rem;margin-bottom:18px;">
                <li>If you did not authorize these transactions, please contact us immediately.</li>
                <li>Keep this email for your records.</li>
            </ul>
            <div style="text-align:center;color:#52b788;font-size:0.98rem;">
                Need help? Contact <a href="mailto:beinvestmentfirm@gmail.com" style="color:#38b000;">
                    beinvestmentfirm@gmail.com
                </a>
            </div>
        </div>"""
        text_content = "Your BE Investment Firm transactions for yesterday:\n"
        for txn in transactions:
            text_content += f"{txn.transaction_type.capitalize()} | NRs. {txn.purchase_initiated_amount:,.2f} | {txn.date_time.strftime('%Y-%m-%d %H:%M')} | ID: {txn.id}\n"

        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
