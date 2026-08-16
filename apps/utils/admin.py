from django.contrib import admin
from .models import Notification, PurchaseReceipt, GiftReceipt, UsageReceipt

admin.site.register(Notification)
admin.site.register(PurchaseReceipt)
admin.site.register(GiftReceipt)
admin.site.register(UsageReceipt)