from django.utils import timezone
from datetime import timedelta
from .models import Transaction
from django.contrib import messages
from .models import BankAccount
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.contrib import messages

PREMIUM_PRICES = {
    'premium': 80,
    'premium_pro': 100,
}

def buy_premium(account: BankAccount, new_type: str):
    price = PREMIUM_PRICES[new_type]
    
    if account.balance < price:
        messages.error(request, "No tienes suficientes galeones para esta cuenta.")

    account.account_type = new_type
    account.upgraded_at = timezone.now()
    account.balance -= price
    account.save()

    messages.success(request, f"Has comprado una cuenta {account.account_type} por {price} galeones.")



def validate_transaction(sender_account, receiver_account, amount):
    if amount < 20:
        messages.error(request, "La transferencia mínima es de 20 galeones.")

    if sender_account.is_frozen:
        messages.error(request, "La cuenta del remitente está congelada.")

    if receiver_account.is_frozen:
        messages.error(request, "La cuenta del receptor está congelada.")

    total_needed = int(amount * 1.05)
    if sender_account.balance < total_needed:
        messages.error(request, "Saldo insuficiente para cubrir: monto + comisión del 5%.")

    if sender_account.weekly_transactions_left <= 0:
        messages.error(request, "El remitente ya realizó su transferencia semanal.")

    if receiver_account.weekly_transactions_left <= 0:
        raise ValidationError("El receptor ya recibió su transferencia semanal.")

    return True


def execute_transaction(sender_account, receiver_account, amount, tx_instance):
    validate_transaction(sender_account, receiver_account, amount)

    with db_transaction.atomic():
        sender_account.balance -= int(amount * 1.05)
        sender_account.weekly_transactions_left -= 1
        sender_account.save()

        receiver_account.balance += amount
        receiver_account.weekly_transactions_left -= 1
        receiver_account.save()

        tx_instance.save()

        messages.success(request, f"Transferencia exitosa.")
        return tx_instance
