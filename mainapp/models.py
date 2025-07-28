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
    share_symbol = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        help_text="Stock symbol for share market investments (e.g., NABIL, NICA, etc.)"
    )

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
    stock_units_purchased = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Units of stock")

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
    email = models.EmailField()
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

class WithdrawalRequest(models.Model):
    """
    Model to track withdrawal requests from users
    Handles complete withdrawal workflow from request to completion
    """
    # Status choices for withdrawal workflow
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processed', 'Processed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Priority levels for fund manager
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Withdrawal type
    WITHDRAWAL_TYPE_CHOICES = [
        ('partial', 'Partial Withdrawal'),
        ('full', 'Full Withdrawal'),
        ('emergency', 'Emergency Withdrawal'),
    ]
    
    # === CORE IDENTIFICATION ===
    withdrawal_id = models.CharField(max_length=20, unique=True, editable=False)  # Auto-generated ID
    authorized_user = models.ForeignKey(
        AuthorizedUser,
        to_field='email',
        db_column='user_email',
        on_delete=models.CASCADE,
        related_name='withdrawal_requests'
    )
    

    # === USER PERSPECTIVE ===
    requested_amount = models.DecimalField(
        max_digits=14, 
        decimal_places=2,
        help_text="Amount requested by user"
    )
    withdrawal_type = models.CharField(
        max_length=20, 
        choices=WITHDRAWAL_TYPE_CHOICES, 
        default='partial'
    )
    # Reference to existing bank details
    bank_detail = models.ForeignKey(
        UserBankDetail,
        on_delete=models.PROTECT,
        related_name='withdrawal_requests',
        help_text="Bank account to transfer withdrawal amount"
    )
    user_reason = models.TextField(blank=True, null=True, help_text="User's reason for withdrawal")
    
    # === SYSTEM PERSPECTIVE ===
    request_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    available_balance_at_request = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        help_text="User's available balance when request was made"
    )
    available_units_at_request = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="User's available units when request was made"
    )
    current_nav_at_request = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="NAV value when request was made"
    )
    
    # === FUND MANAGER PERSPECTIVE ===
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    reviewed_by = models.CharField(max_length=100, blank=True, null=True)
    reviewed_date = models.DateTimeField(blank=True, null=True)
    approved_amount = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Amount approved by fund manager (may differ from requested)"
    )
    manager_notes = models.TextField(
        blank=True, 
        null=True, 
        help_text="Fund manager's internal notes"
    )
    rejection_reason = models.TextField(
        blank=True, 
        null=True, 
        help_text="Reason for rejection if applicable"
    )
    
    # === PROCESSING & COMPLETION ===
    processed_by = models.CharField(max_length=100, blank=True, null=True)
    processed_date = models.DateTimeField(blank=True, null=True)
    actual_processed_amount = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Actual amount processed and transferred"
    )
    units_redeemed = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Number of units redeemed for this withdrawal"
    )
    processing_fee = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0,
        help_text="Any processing fees deducted"
    )
    
    # === AUDIT & TRACKING ===
    created_from_ip = models.GenericIPAddressField(blank=True, null=True)
    supporting_documents = models.FileField(
        upload_to='withdrawal_documents/', 
        blank=True, 
        null=True,
        help_text="Any supporting documents uploaded by user"
    )
    completion_receipt = models.FileField(
        upload_to='withdrawal_receipts/', 
        blank=True, 
        null=True,
        help_text="Receipt or proof of transfer"
    )
    
    # === RISK & COMPLIANCE ===
    requires_manual_review = models.BooleanField(
        default=False,
        help_text="Flag for withdrawals requiring manual review"
    )
    risk_score = models.IntegerField(
        default=0,
        help_text="Risk score for this withdrawal (0-100)"
    )
    compliance_checked = models.BooleanField(default=False)
    compliance_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-request_date']
        indexes = [
            models.Index(fields=['status', 'request_date']),
            models.Index(fields=['authorized_user', 'status']),
            models.Index(fields=['priority', 'request_date']),
        ]
    
    def save(self, *args, **kwargs):
        # Auto-generate withdrawal ID if not set
        if not self.withdrawal_id:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.withdrawal_id = f"WD{timestamp}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Withdrawal {self.withdrawal_id} - {self.authorized_user.email} - NRs. {self.requested_amount}"
    
    @property
    def is_pending(self):
        return self.status in ['pending', 'under_review']
    
    @property
    def is_actionable(self):
        return self.status in ['pending', 'under_review', 'approved']
    
    @property
    def can_be_cancelled(self):
        return self.status in ['pending', 'under_review']
    
    @property
    def processing_time_days(self):
        if self.processed_date and self.request_date:
            return (self.processed_date - self.request_date).days
        return None
