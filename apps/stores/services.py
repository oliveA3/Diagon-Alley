from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Store, Product, WarehouseItem, InventoryItem
from apps.users.models import CustomUser
from apps.utils import utils
from django.db import transaction as db_transaction
from apps.bank.models import BankAccount
from django.db.models import Max
from decimal import Decimal
from django.utils import timezone


def add_product_to_inventory(request, user: CustomUser, product: Product):
    warehouse_i = WarehouseItem.objects.get(product_id=product.id)
    inventory_i = InventoryItem.objects.filter(
        user_id=user.id, product_id=product.id).first()
    added = False

    if warehouse_i and warehouse_i.available:
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

        if added and warehouse_i.stock and warehouse_i.stock > 0:
            warehouse_i.stock -= 1
            if warehouse_i.stock == 0:
                warehouse_i.available = False
            warehouse_i.save()
        return added

    else:
        messages.error(
            request, "Este artículo no está disponible por hoy.")
        return added


def get_discount(user):
    discounts_qs = InventoryItem.objects.filter(
        user=user,
        product__discount__isnull=False
    ).exclude(product__discount=0)

    if discounts_qs.exists():
        return discounts_qs.aggregate(Max('product__discount'))['product__discount__max'] or Decimal('0.0')

    return Decimal('0.0')


def apply_discount(price, discount):
    price_to_pay = price
    if discount > 0:
        price_to_pay = int(price - (price * discount))

    return price_to_pay


def purchase_product(request, user, account, product: Product, discount):
    price_to_pay = apply_discount(product.price, discount)

    if account.balance >= price_to_pay:
        with db_transaction.atomic():
            if add_product_to_inventory(request, user, product):
                account.balance -= price_to_pay
                account.last_pur_date = timezone.now().date()
                utils.generate_purchase_receipt(user, product, 'purchase', price_to_pay)

                if account.is_frozen:
                    account.is_frozen = False
                account.save()

                messages.success(
                    request, f"Has comprado {product.name} por {price_to_pay} galeones.")
    else:
        messages.error(
            request, "No tienes suficientes galeones para comprar este artículo.")


def gift_product(request, sender_account: BankAccount, receiver: CustomUser, product_id: int, discount):
    product = get_object_or_404(Product, id=product_id)
    total_cost = apply_discount(product.price, discount) + 5

    if sender_account.balance >= total_cost:
        with db_transaction.atomic():
            if add_product_to_inventory(request, receiver, product):
                sender_account.balance -= total_cost
                utils.generate_purchase_receipt(sender_account.user, product, 'gift', total_cost)
                sender.last_pur_date = timezone.now().date()

                if sender_account.is_frozen:
                    sender_account.is_frozen = False
                sender_account.save()

                receiver_account = receiver.bank_account
                if receiver_account.is_frozen:
                    receiver_account.is_frozen = False
                    receiver_account.save()
                
                messages.success(
                    request, f"Has regalado {product.name} a {receiver.username} (Cuenta No. {receiver.id}).")

    else:
        messages.error(
            request, "No tienes suficientes galeones para regalar este artículo.")
