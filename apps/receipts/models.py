from django.db import models
from django.utils import timezone

class BaseReceipt(models.Model):
    code = models.CharField(max_length=8, unique=True)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class PurchaseReceipt(BaseReceipt):
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='purchase_receipts'
    )
    product = models.ForeignKey(
        'stores.Product',
        on_delete=models.SET_NULL,
        null=True,
        related_name='purchase_receipts'
    )
    price = models.PositiveIntegerField()


class UsageReceipt(BaseReceipt):
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='usage_receipts'
    )
    product = models.ForeignKey(
        'stores.Product',
        on_delete=models.SET_NULL,
        null=True,
        related_name='usage_receipts'
    )
    uses_left = models.PositiveIntegerField()
