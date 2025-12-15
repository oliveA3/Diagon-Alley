from django.utils import timezone
from apps.stores.models import WarehouseItem, InventoryItem
from apps.bank.models import BankAccount, Transaction
from apps.users.models import CustomUser

def clear_inventory():
    expired_items = InventoryItem.objects.filter(expiration_date__lt=timezone.now())
    count = expired_items.count()
    expired_items.delete()
    return count