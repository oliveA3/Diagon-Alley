from django.shortcuts import get_object_or_404, redirect, render
from apps.users.models import CustomUser
from apps.stores.models import Store, Product, WarehouseItem, InventoryItem
from django.contrib import messages
from datetime import date


def grant_product(request, user: CustomUser, product: Product):
    inventory_i = InventoryItem.objects.filter(
        user_id=user.id, product_id=product.id).first()
    added = False

    # It's already in the inventory
    if inventory_i:
        if product.product_type in ['broom', 'wand']:
            inventory_i.uses += product.uses
            inventory_i.pur_date = date.today()
            inventory_i.save()
            added = True

        elif product.product_type in ['pet', 'wheezes']:
            if request.user == user:
                messages.error(
                    request, f"Solo puedes tener uno de estos artículos en tu inventario.")

            else:
                messages.error(
                    request, f"Este artículo ya está en el inventario de {user.username} y no es acumulable.")

            return added

    # Not in the inventory
    else:
        InventoryItem.objects.create(
            user=user,
            product=product,
            store=product.store,
            pur_date=date.today(),
            uses=product.uses,
        )
        added = True

    return added