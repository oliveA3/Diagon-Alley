from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Store, Product, WarehouseItem, InventoryItem
from apps.receipts import utils


def purchase_product(request, user, account, product, store, discount):
    price_to_pay = product.price
    if discount:
        price_to_pay = int(product.price * 0.9)

    if account.balance >= price_to_pay:
        warehouse_item = get_object_or_404(
            WarehouseItem, product_id=product.id, store_id=store.id)
        inventory_items = InventoryItem.objects.select_related(
            'product').filter(user_id=user.id)

        if warehouse_item.available:
            in_inventory = False
            new_uses = product.uses

            try:
                old_item = inventory_items.get(product_id=product.id)
                in_inventory = True
            except InventoryItem.DoesNotExist:
                old_item = None

            if not in_inventory or (in_inventory and product.stackable):
                if in_inventory and product.stackable:
                    new_uses += old_item.uses
                    old_item.delete()

                InventoryItem.objects.create(
                    user_id=request.user.id,
                    product_id=product.id,
                    store_id=store.id,
                    pur_date=date.today(),
                    uses=new_uses,
                )

                if warehouse_item.stock:
                    warehouse_item.stock -= 1
                    if warehouse_item.stock == 0:
                        warehouse_item.available = False
                        warehouse_item.save()

                account.balance -= price_to_pay

                if account.is_frozen:
                    account.is_frozen = False

                account.save()
                
                receipt = utils.generate_purchase_receipt(user, product, price_to_pay)
                message = utils.generate_purchase_message(receipt)
                
                messages.success(
                    request, f"Has comprado {product.name} por {price_to_pay} galeones.")
                return message

            elif in_inventory and not product.stackable:
                messages.error(
                    request, "Solo puedes tener uno de estos artículos en tu inventario.")

            elif warehouse_item.stock == 0:
                messages.error(
                    request, "Este artículo se ha agotado por hoy.")

        else:
            messages.error(
                request, "Este artículo ya no está disponible.")

    else:
        messages.error(
            request, "No tienes suficientes galeones para comprar este artículo.")
