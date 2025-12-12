from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Store, Product, WarehouseItem, InventoryItem
from apps.users.models import CustomUser
from apps.utils import utils
from django.db import transaction as db_transaction
from apps.bank.models import BankAccount
from django.db.models import Max


def get_discount(user):
    discounts_qs = InventoryItem.objects.filter(
        user=user,
        product__discount__isnull=False
    ).exclude(
        product__discount=0
    )

    discount = 0.0
    if discounts_qs.exists():
        discount = discounts_qs.aggregate(Max('product__discount'))[
            'product__discount__max']

    return discount


def apply_discount(price, discount):
    price_to_pay = price
    if discount != 0.0:
        price_to_pay = int(price - (price * discount))

    return price_to_pay


def purchase_product(request, user, account, product: Product, discount, store: Store):
    price_to_pay = apply_discount(product.price, discount)

    if account.balance >= price_to_pay:
        with db_transaction.atomic():
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

                    receipt = utils.generate_purchase_receipt(
                        user, product, price_to_pay)
                    message = utils.generate_purchase_message(receipt)

                    messages.success(
                        request, f"Has comprado {product.name} por {price_to_pay} galeones.")
                    return message

                elif in_inventory and not product.stackable:
                    messages.error(
                        request, "Solo puedes tener uno de estos artículos en tu inventario.")

            else:
                messages.error(
                    request, "Este artículo ya no está disponible hoy.")
    else:
        messages.error(
            request, "No tienes suficientes galeones para comprar este artículo.")


def gift_product(request, sender_account: BankAccount, receiver: CustomUser, product_id: int, discount, store: Store):
    product = get_object_or_404(Product, id=product_id)
    total_cost = apply_discount(product.price, discount) + 5

    if sender_account.balance >= total_cost:
        with db_transaction.atomic():
            warehouse_item = get_object_or_404(
                WarehouseItem, product_id=product_id, store_id=store.id)
            inventory_items = InventoryItem.objects.select_related(
                'product').filter(user_id=receiver.id)

            if warehouse_item.available:
                in_inventory = False
                new_uses = product.uses

                try:
                    old_item = inventory_items.get(product_id=product_id)
                    in_inventory = True
                except InventoryItem.DoesNotExist:
                    old_item = None

                if not in_inventory or (in_inventory and product.stackable):
                    if in_inventory and product.stackable:
                        new_uses += old_item.uses
                        old_item.delete()

                    InventoryItem.objects.create(
                        user_id=receiver.id,
                        product_id=product_id,
                        store_id=store.id,
                        uses=new_uses,
                    )

                    if warehouse_item.stock:
                        warehouse_item.stock -= 1
                        if warehouse_item.stock == 0:
                            warehouse_item.available = False
                        warehouse_item.save()

                    sender_account.balance -= price_to_pay
                    if sender_account.is_frozen:
                        sender_account.is_frozen = False
                    sender_account.save()

                    messages.success(
                        request, f"Has regalado {product.name} a {receiver.username} (Cuenta No. {receiver.id}).")
                    return message

                elif in_inventory and not product.stackable:
                    messages.error(
                        request, "El usuario seleccionado ya tiene este artículo en su inventario y no es acumulable.")

            else:
                messages.error(
                    request, "Este artículo ya no está disponible hoy.")
    else:
        messages.error(
            request, "No tienes suficientes galeones para regalar este artículo.")
