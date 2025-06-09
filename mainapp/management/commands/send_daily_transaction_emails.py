from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from mainapp.models import UserTransaction, AuthorizedUser
from django.conf import settings

class Command(BaseCommand):
    help = "Send daily transaction summary emails to users"

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        users = AuthorizedUser.objects.all()
        for user in users:
            transactions = UserTransaction.objects.filter(
                authorized_user=user,
                date_time__date=today
            )
            if transactions.exists():
                subject = "Your Transaction Summary"
                message = render_to_string('mainapp/daily_transaction_email.txt', {
                    'user_email': user.email,
                    'transactions': transactions,
                    'date': today
                })
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )