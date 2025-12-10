from django.db import models
from datetime import timedelta
from django.utils import timezone
from apps.users.models import CustomUser


class BankAccount(models.Model):
    id = models.PositiveIntegerField(primary_key=True, unique=True)
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'student'}, related_name='bank_account')

    balance = models.IntegerField(default=20)
    is_frozen = models.BooleanField(default=False)

    ACCOUNT_TYPES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('premium_pro', 'Premium Pro'),
    ]
    account_type = models.CharField(choices=ACCOUNT_TYPES, default='standard')

    created_at = models.DateField(auto_now=True)
    upgraded_at = models.DateField(null=True, blank=True)

    weekly_transactions_left = models.PositiveIntegerField(default=1)

    @property
    def current_limit(self):
        return {
            'standard': 200,
            'premium': 300,
            'premium_pro': 400,

        }.get(self.account_type, 200)

    @property
    def premium_ex_date(self):
        if not self.upgraded_at or self.account_type == 'standard':
            return None
        
        if self.account_type == 'premium':
            return self.upgraded_at + timedelta(days=90)
        
        if self.account_type == 'premium_pro':
            return self.upgraded_at + timedelta(days=180)
        
        return None

    def check_expiration(self):
        if self.account_type == 'premium' and self.upgraded_at:
            if timezone.now().date() > self.upgraded_at + timedelta(days=90):
                self.account_type = 'standard'
                self.upgraded_at = None
                self.save()

        elif self.account_type == 'premium_pro' and self.upgraded_at:
            if timezone.now().date() > self.upgraded_at + timedelta(days=180):
                self.account_type = 'standard'
                self.upgraded_at = None
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
    amount = models.PositiveIntegerField(default=20)
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
