from django.db import models
from datetime import timedelta
from django.utils import timezone
from apps.users.models import CustomUser


class BankAccount(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='bank_account',
        primary_key=True
    )

    balance = models.IntegerField(default=20)
    last_pur_date = models.CharField(null=True, blank=True)
    
    is_frozen = models.BooleanField(default=False)
    frozen_date = models.DateField(null=True, blank=True)

    ACCOUNT_TYPES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ]
    account_type = models.CharField(choices=ACCOUNT_TYPES, default='standard')

    created_at = models.DateField(auto_now_add=True)
    upgraded_at = models.DateField(null=True, blank=True)
    # Just for premium
    duration_days = models.PositiveIntegerField(null=True, blank=True)

    weekly_transactions_left = models.PositiveIntegerField(default=1)
    last_trans_date = models.DateField(null=True, blank=True)

    @property
    def current_limit(self):
        if self.account_type == 'vip':
            return None
        return {
            'standard': 200,
            'premium': 400,
        }.get(self.account_type, 200)

    @property
    def premium_ex_date(self):
        if self.account_type in ['vip', 'standard']:
            return None
        elif self.account_type == 'premium':
            return self.upgraded_at + timedelta(days=self.duration_days)
        return None


class Transaction(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.PositiveIntegerField(default=20)
    created_at = models.DateField(auto_now_add=True)


class Loan(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='loans_requested')
    codebtor_a = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='loans_as_codebtor_a',
        null=True, blank=True
    )
    codebtor_b = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='loans_as_codebtor_b',
        null=True, blank=True
    )

    LOAN_CHOICES = [
        (0, "25 → 30"),
        (1, "50 → 60"),
        (2, "100 → 120"),
    ]
    loan_type = models.IntegerField(choices=LOAN_CHOICES)

    amount_requested = models.PositiveIntegerField()
    amount_due = models.PositiveIntegerField()

    approved = models.BooleanField(default=False)
    approved_at = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)

    STATES = [
        ('pending', "Pendiente"),
        ('paid', "Pagado"),
    ]
    state = models.CharField(max_length=10, choices=STATES, default='pending')

    def __str__(self):
        return f"Préstamo de {self.amount_requested} galeones a {self.user.full_name}"

    @property
    def due_date(self):
        if not self.approved_at:
            return None

        if self.loan_type == 0:
            return self.approved_at + timedelta(days=30)
        elif self.loan_type == 1:
            return self.approved_at + timedelta(days=60)
        elif self.loan_type == 2:
            return self.approved_at + timedelta(days=90)

    @property
    def is_overdue(self):
        return self.due_date and timezone.now().date() > self.due_date
    
    @property
    def is_near_due(self):
        if not self.due_date:
            return False
        
        delta = self.due_date - timezone.now().date()
        return 0 <= delta.days <= 4
