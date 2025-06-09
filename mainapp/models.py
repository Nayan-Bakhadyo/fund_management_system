from django.db import models

# Create your models here.

class AuthorizedUser(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('fund_manager', 'Fund Manager'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

class UserTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]
    authorized_user = models.ForeignKey(
        AuthorizedUser,
        to_field='email',
        db_column='email',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    date_time = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, default='Withdrawal')
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    purchase_initiated_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    purchase_unit = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_credit = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_image = models.ImageField(upload_to='transaction_images/', null=True, blank=True)  # <-- Added field

    def __str__(self):
        return f"Transaction for {self.authorized_user.email} on {self.date_time.strftime('%Y-%m-%d %H:%M:%S')}"

class UserNAV(models.Model):
    authorized_user = models.OneToOneField(
        AuthorizedUser,
        to_field='email',
        db_column='email',
        on_delete=models.CASCADE,
        related_name='nav'
    )
    available_unit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    available_credit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"NAV for {self.authorized_user.email}: Units={self.available_unit}, Credit={self.available_credit_amount}"

class NAVRecord(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)

    def __str__(self):
        return f"NAV on {self.date_time.strftime('%Y-%m-%d %H:%M:%S')}: Unit Cost {self.unit_cost}"
