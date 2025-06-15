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
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    investment_id = models.AutoField(primary_key=True)
    investment_name = models.CharField(max_length=100)
    investment_category = models.ForeignKey(
        InvestmentCategory,
        on_delete=models.CASCADE,
        related_name='investments'
    )
    invested_amount = models.DecimalField(max_digits=14, decimal_places=2)
    return_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default='open')

    def __str__(self):
        return f"{self.investment_name} ({self.get_status_display()})"

class TotalCapitalRecord(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    total_capital = models.DecimalField(max_digits=16, decimal_places=2)
    invested_capital = models.DecimalField(max_digits=16, decimal_places=2)
    available_capital = models.DecimalField(max_digits=16, decimal_places=2)
    total_circulating_unit = models.IntegerField(default=0) 

    def __str__(self):
        return f"Total Capital on {self.date_time.strftime('%Y-%m-%d %H:%M:%S')}: {self.total_capital}"
