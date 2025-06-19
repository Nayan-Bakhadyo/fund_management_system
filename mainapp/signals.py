from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import (
    AuditLog, UserTransaction, UserTransactionUpload, TotalCapitalRecord,
    FirmInvestment, InvestmentTransaction, UserRecurringPayment, AuthorizedUser,
    UserNAV
)
import threading

# Helper to get user from thread local (if you want to set it in middleware)
_user = threading.local()

def get_current_user():
    return getattr(_user, 'value', None)

def set_current_user(user):
    _user.value = user

# --- Signal Handlers ---

def log_action(instance, action, triggered_by, extra_message=None):
    AuditLog.objects.create(
        table_name=instance.__class__.__name__,
        object_id=str(getattr(instance, 'id', '') or getattr(instance, 'pk', '')),
        action=action,
        changed_by=get_current_user() or '',  # Set via middleware if you want user info
        change_message=extra_message or str(instance),
        triggered_by=triggered_by
    )

@receiver(post_save, sender=UserTransaction)
def log_usertransaction_save(sender, instance, created, **kwargs):
    log_action(
        instance,
        'CREATE' if created else 'UPDATE',
        'signal:post_save',
        f"{'Created' if created else 'Updated'} UserTransaction: {instance}"
    )

@receiver(post_delete, sender=UserTransaction)
def log_usertransaction_delete(sender, instance, **kwargs):
    log_action(
        instance,
        'DELETE',
        'signal:post_delete',
        f"Deleted UserTransaction: {instance}"
    )

@receiver(post_save, sender=UserTransactionUpload)
def log_usertransactionupload_save(sender, instance, created, **kwargs):
    log_action(
        instance,
        'CREATE' if created else 'UPDATE',
        'signal:post_save',
        f"{'Created' if created else 'Updated'} UserTransactionUpload: {instance}"
    )

@receiver(post_delete, sender=UserTransactionUpload)
def log_usertransactionupload_delete(sender, instance, **kwargs):
    log_action(
        instance,
        'DELETE',
        'signal:post_delete',
        f"Deleted UserTransactionUpload: {instance}"
    )

@receiver(post_save, sender=TotalCapitalRecord)
def log_totalcapitalrecord_save(sender, instance, created, **kwargs):
    log_action(
        instance,
        'CREATE' if created else 'UPDATE',
        'signal:post_save',
        f"{'Created' if created else 'Updated'} TotalCapitalRecord: {instance}"
    )

@receiver(post_delete, sender=TotalCapitalRecord)
def log_totalcapitalrecord_delete(sender, instance, **kwargs):
    log_action(
        instance,
        'DELETE',
        'signal:post_delete',
        f"Deleted TotalCapitalRecord: {instance}"
    )

@receiver(post_save, sender=FirmInvestment)
def log_firminvestment_save(sender, instance, created, **kwargs):
    log_action(
        instance,
        'CREATE' if created else 'UPDATE',
        'signal:post_save',
        f"{'Created' if created else 'Updated'} FirmInvestment: {instance}"
    )

@receiver(post_delete, sender=FirmInvestment)
def log_firminvestment_delete(sender, instance, **kwargs):
    log_action(
        instance,
        'DELETE',
        'signal:post_delete',
        f"Deleted FirmInvestment: {instance}"
    )

@receiver(post_save, sender=InvestmentTransaction)
def log_investmenttransaction_save(sender, instance, created, **kwargs):
    log_action(
        instance,
        'CREATE' if created else 'UPDATE',
        'signal:post_save',
        f"{'Created' if created else 'Updated'} InvestmentTransaction: {instance}"
    )

@receiver(post_delete, sender=InvestmentTransaction)
def log_investmenttransaction_delete(sender, instance, **kwargs):
    log_action(
        instance,
        'DELETE',
        'signal:post_delete',
        f"Deleted InvestmentTransaction: {instance}"
    )

@receiver(post_save, sender=UserRecurringPayment)
def log_userrecurringpayment_save(sender, instance, created, **kwargs):
    log_action(
        instance,
        'CREATE' if created else 'UPDATE',
        'signal:post_save',
        f"{'Created' if created else 'Updated'} UserRecurringPayment: {instance}"
    )

@receiver(post_delete, sender=UserRecurringPayment)
def log_userrecurringpayment_delete(sender, instance, **kwargs):
    log_action(
        instance,
        'DELETE',
        'signal:post_delete',
        f"Deleted UserRecurringPayment: {instance}"
    )

@receiver(post_save, sender=AuthorizedUser)
def log_authorizeduser_save(sender, instance, created, **kwargs):
    log_action(
        instance,
        'CREATE' if created else 'UPDATE',
        'signal:post_save',
        f"{'Created' if created else 'Updated'} AuthorizedUser: {instance}"
    )

@receiver(post_delete, sender=AuthorizedUser)
def log_authorizeduser_delete(sender, instance, **kwargs):
    log_action(
        instance,
        'DELETE',
        'signal:post_delete',
        f"Deleted AuthorizedUser: {instance}"
    )

@receiver(post_save, sender=UserNAV)
def log_usernav_save(sender, instance, created, **kwargs):
    log_action(
        instance,
        'CREATE' if created else 'UPDATE',
        'signal:post_save',
        f"{'Created' if created else 'Updated'} UserNAV: {instance}"
    )

@receiver(post_delete, sender=UserNAV)
def log_usernav_delete(sender, instance, **kwargs):
    log_action(
        instance,
        'DELETE',
        'signal:post_delete',
        f"Deleted UserNAV: {instance}"
    )