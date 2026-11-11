from apps.stores.models import InventoryItem
from apps.users.models import CustomUser
from apps.utils import utils
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404


def filter_inventory(query, inventory):
    for key, items in inventory.items():
        items = items.filter(product__name__icontains=query)
        inventory[key] = items

    return inventory


def use_inventory_item(item_id: int, user: CustomUser):
    with db_transaction.atomic():
        item = get_object_or_404(
            InventoryItem.objects.select_for_update(), id=item_id, user=user)
        result = item.use()

        if result == 'empty':
            return None

        receipt = utils.generate_usage_receipt(user, item)

        return receipt
