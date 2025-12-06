from django.dispatch import receiver
from django.db.models.signals import post_migrate
from apps.stores.models import WarehouseItem, InventoryItem
from apps.users.models import CustomUser
from apps.bank.models import BankAccount


@receiver(post_migrate)
def startup_updates(sender, **kwargs):
    for account in BankAccount.objects.all():
        account.check_account_expiration()
        
    for frozen in BankAccount.objects.filter(is_frozen=True):
        frozen.frozen_discount()
    
    for item in WarehouseItem.objects.all():
        item.update_stock()
        
    for item in InventoryItem.objects.all():
        item.update_inventory()
    
        
