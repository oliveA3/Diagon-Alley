import uuid
from apps.users.models import CustomUser
from apps.stores.models import Product, InventoryItem
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


def generate_purchase_receipt(user: CustomUser, product: Product, p_type: str, price: int):
    receipt_code = str(uuid.uuid4())[:8].upper()

    receipt = PurchaseReceipt.objects.create(
        code=receipt_code,
        user=user,
        product_id=product.id,
        purchase_type=p_type,
        price=price
    )

    return receipt


def generate_usage_receipt(user: CustomUser, inventory_item: InventoryItem):
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
        "🧙‍♂🪄🧙‍♂🪄🧙‍♂🪄🧙‍♂🪄🧙‍♂🪄🧙‍♂🪄🧙‍♂\n"
        "•🪙💰🪙💰🪙💰🪙💰🪙💰🪙• \n\n"
        f"Ticket de Uso\n"
        f"🧾 Código: {receipt.code}\n"
        f"✅ Dueño: {receipt.user.full_name}\n"
        f"💳 No. de cuenta: {account.pk}\n"
        f"🪄 Producto: {receipt.product.name}\n"
        f"🚀 Usos restantes: {receipt.uses_left}\n"
        f"🗓 Fecha: {receipt.created_at.strftime('%d/%m/%Y %H:%M')}\n\n"
        "•🪙💰🪙💰🪙💰🪙💰🪙💰🪙•\n"
        "🧙‍♂🪄🧙‍♂🪄🧙‍♂🪄🧙‍♂🪄🧙‍♂🪄🧙‍♂🪄🧙‍♂"
    )

    return message
