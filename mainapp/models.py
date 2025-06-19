from django.db import models

# Create your models here.

class AuthorizedUser(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('fund_manager', 'Fund Manager'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_contracted = models.BooleanField(default=False)  # <-- Added field

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
    transaction_image = models.ImageField(upload_to='transaction_images/', null=True, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)  

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
    
class UserBankDetail(models.Model):
    authorized_user = models.OneToOneField(
        AuthorizedUser,
        to_field='email',
        db_column='email',
        on_delete=models.CASCADE,
        related_name='bank_detail'
    )
    bank_number = models.BigIntegerField()
    bank_name = models.CharField(max_length=100)
    account_holder_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    cell_number = models.CharField(max_length=20)

    def __str__(self):
        return f"Bank details for {self.authorized_user.email} ({self.bank_name})"

class UserContract(models.Model):
    authorized_user = models.OneToOneField(
        AuthorizedUser,
        to_field='email',
        db_column='email',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='contract'
    )
    contract_pdf_img = models.FileField(upload_to='contracts/', null=True, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)

class UserRecurringPayment(models.Model):
    authorized_user = models.ForeignKey(
        AuthorizedUser,
        to_field='email',
        db_column='email',
        on_delete=models.CASCADE,
        related_name='recurring_payments'
    )
    recurring_payment_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Contract for {self.authorized_user.email}"

class InvestmentCategory(models.Model):
    RISK_FACTOR_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    TIMEFRAME_CHOICES = [
        ('Short Term', 'Short Term'),
        ('Medium Term', 'Medium Term'),
        ('Long Term', 'Long Term'),
    ]
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)
    category_description = models.TextField(blank=True, null=True)
    category_risk_factor = models.CharField(max_length=6, choices=RISK_FACTOR_CHOICES)
    category_time_frame = models.CharField(max_length=20, choices=TIMEFRAME_CHOICES)

    def __str__(self):
        return f"{self.category_name} ({self.category_risk_factor})"

class FirmInvestment(models.Model):
    investment_id = models.AutoField(primary_key=True)
    investment_name = models.CharField(max_length=100)
    investment_category = models.ForeignKey(
        InvestmentCategory,
        on_delete=models.CASCADE,
        related_name='investments'
    )
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default='open')

    def __str__(self):
        return f"{self.investment_name}"

class InvestmentTransaction(models.Model):
    AMOUNT_TYPE_CHOICES = [
        ('investment', 'Investment'),
        ('return', 'Return'),
    ]
    investment = models.ForeignKey(
        FirmInvestment,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    amount_type = models.CharField(max_length=11, choices=AMOUNT_TYPE_CHOICES)

    def __str__(self):
        return f"{self.investment.investment_name} - {self.get_amount_type_display()} - {self.amount}"

class TotalCapitalRecord(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    total_capital = models.DecimalField(max_digits=16, decimal_places=2)
    invested_capital = models.DecimalField(max_digits=16, decimal_places=2)
    available_capital = models.DecimalField(max_digits=16, decimal_places=2)
    total_circulating_unit = models.IntegerField(default=0) 

    def __str__(self):
        return f"Total Capital on {self.date_time.strftime('%Y-%m-%d %H:%M:%S')}: {self.total_capital}"

class UserTransactionUpload(models.Model):
    email = models.EmailField(primary_key=True)
    date_time = models.DateTimeField(auto_now_add=True)
    transaction_file = models.FileField(upload_to='user_transaction_uploads/', null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_valid = models.BooleanField(default=True)
    is_credited = models.BooleanField(default=False)

    def __str__(self):
        return f"Transaction upload by {self.email} on {self.date_time.strftime('%Y-%m-%d %H:%M:%S')}"

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('OTHER', 'Other'),
    ]
    table_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    changed_by = models.CharField(max_length=100, blank=True, null=True)
    change_message = models.TextField()
    triggered_by = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.table_name} {self.action} by {self.changed_by} at {self.timestamp}"
