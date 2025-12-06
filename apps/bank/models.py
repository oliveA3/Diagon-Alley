from django.db import models
from datetime import timedelta
from django.utils import timezone
from apps.users.models import CustomUser


class BankAccount(models.Model):
    id = models.PositiveIntegerField(primary_key=True, unique=True)
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='bank_account')

    # Fields for students
    balance = models.IntegerField(default=0, null=True, blank=True)
    is_frozen = models.BooleanField(default=False, null=True, blank=True)

    ACCOUNT_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('premium_pro', 'Premium Pro'),
    ]
    account_type = models.CharField(
        max_length=20, choices=ACCOUNT_CHOICES, default='standard'
    )

    limit = models.PositiveIntegerField(default=200)

    premium_start_date = models.DateField(null=True, blank=True)

    daily_transaction_limit = models.PositiveIntegerField(default=1)
    daily_received_limit = models.PositiveIntegerField(default=1)

    def frozen_discount(self):
        if self.is_frozen:
            self.balance = int(self.balance * 0.96)

    def check_account_expiration(self):
        if self.account_type == 'standard':
            return

        if not self.premium_start_date:
            return

        now = timezone.now().date()
        delta = now - self.premium_start_date

        if self.account_type == 'premium' and delta >= timedelta(days=90):
            self.account_type = 'standard'
            self.premium_start_date = None
            self.limit = 200
            self.balance = min(self.balance, self.limit)
            self.save()

        elif self.account_type == 'premium_pro' and delta >= timedelta(days=180):
            self.account_type = 'standard'
            self.premium_start_date = None
            self.limit = 200
            self.balance = min(self.balance, self.limit)
            self.save()

    def save(self, *args, **kwargs):
        if not self.id:
            used_ids = set(BankAccount.objects.values_list('id', flat=True))
            i = 1
            while i in used_ids:
                i += 1
            self.id = i
        super().save(*args, **kwargs)


class Transaction(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} ({self.amount} galeones)"


class Loan(models.Model):
    LOAN_CHOICES = [
        (0, "25 galeones → 30 galeones"),
        (1, "50 galeones → 60 galeones"),
        (2, "100 galeones → 120 galeones"),
    ]
    loan_type = models.IntegerField(choices=LOAN_CHOICES)
    
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='loans_requested'
    )
    codebtor_a = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='loans_as_codebtor_a'
    )
    codebtor_b = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='loans_as_codebtor_b'
    )

    amount_requested = models.PositiveIntegerField()
    amount_due = models.PositiveIntegerField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)

    def approve(self):
        self.approved = True
        self.due_date = timezone.now().date() + timezone.timedelta(days=30)
        self.save()

        account = BankAccount.objects.get(user=self.user)
        account.balance += self.amount_requested
        account.save()

    def __str__(self):
        return f"Préstamo de {self.amount_requested} galeones a {self.user.full_name}"
