import uuid
from .models import PurchaseReceipt, UsageReceipt
from apps.bank.models import BankAccount
from datetime import datetime

def working_hours():
    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()  # 0 = monday, 6 = sunday

    # Monday to Friday (0-4) from 6am to 11pm
    working_hours = (0 <= weekday <= 4 and 6 <= hour <= 23)

    return working_hours



def generate_purchase_receipt(user, product, final_price):
    receipt_code = str(uuid.uuid4())[:8].upper()

    receipt = PurchaseReceipt.objects.create(
        code=receipt_code,
        user=user,
        product_id=product.id,
        price=final_price,
    )

    return receipt

def generate_purchase_message(receipt):
    account = BankAccount.objects.get(user_id=receipt.user.id)
    
    message = (
        f"🧾 Ticket de Compra\n"
        f"Código: {receipt.code}\n"
        f"Comprador: {receipt.user.full_name}\n"
        f"No. de cuenta: {account.pk}\n"
        f"Producto: {receipt.product.name}\n"
        f"Precio: {receipt.price} galeones\n"
        f"Fecha: {receipt.created_at.strftime('%d/%m/%Y %H:%M')}"
    )
    
    return message


def generate_usage_receipt(user, inventory_item):
    receipt_code = str(uuid.uuid4())[:8].upper()

    receipt = UsageReceipt.objects.create(
        code=receipt_code,
        user=user,
        product_id=inventory_item.product_id,
        uses_left=inventory_item.uses,
    )

    return receipt


def generate_usage_message(receipt):
    account = BankAccount.objects.get(user_id=receipt.user.id)

    message = (
        f"🧾 Ticket de Uso\n"
        f"Código: {receipt.code}\n"
        f"Comprador: {receipt.user.full_name}\n"
        f"No. de cuenta: {account.pk}\n"
        f"Producto: {receipt.product.name}\n"
        f"Usos restantes: {receipt.uses_left}\n"
        f"Fecha: {receipt.created_at.strftime('%d/%m/%Y %H:%M')}"
    )

    return message
