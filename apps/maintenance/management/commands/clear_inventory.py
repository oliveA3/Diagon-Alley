from django.utils import timezone
from apps.stores.models import InventoryItem

def clear_inventory():
    today = timezone.now().date()
    expired_items = [
        item for item in InventoryItem.objects.all()
        if item.ex_date and item.ex_date < today
    ]
    count = len(expired_items)
    for item in expired_items:
        item.delete()
    return count
