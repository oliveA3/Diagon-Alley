from django.db import models
from django.utils import timezone
from apps.users.models import CustomUser


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateField(auto_now_add=True)


class BaseReceipt(models.Model):
    code = models.CharField(max_length=8, unique=True)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    created_at = models.DateField(default=timezone.now)

    class Meta:
        abstract = True


class UsageReceipt(BaseReceipt):
    product = models.ForeignKey(
        'stores.Product', on_delete=models.SET_NULL, null=True)
    uses_left = models.PositiveIntegerField()
