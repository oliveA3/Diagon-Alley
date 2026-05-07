from django.db import models
from django.utils import timezone
from apps.users.models import CustomUser


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)


class BaseReceipt(models.Model):
    code = models.CharField(max_length=8, unique=True)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    product = models.ForeignKey(
        'stores.Product', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True


class PurchaseReceipt(BaseReceipt):
    price = models.PositiveIntegerField()


class GiftReceipt(BaseReceipt):
    price = models.PositiveIntegerField()
    
    receiver = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gift_receipts'
    )

class UsageReceipt(BaseReceipt):
    uses_left = models.PositiveIntegerField()
