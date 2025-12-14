from django.utils import timezone
from datetime import timedelta
from .models import Transaction
from django.contrib import messages
from .models import BankAccount
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.contrib import messages


def update_balance(self, amount):
    """
    amount > 0 → agregar galeones
    amount < 0 → retirar galeones
    """

    if self.is_frozen:
        messages.error(
            request, "Su cuenta está congelada y no puede recibir galeones.")
        return False

    new_balance = self.balance + amount

    if new_balance < 0:
        messages.error(request, "No cuenta con galeones suficientes.")
        return False

    if new_balance > self.current_limit:
        messages.error(
            request, "Esta cantidad de galeones excede el límite de su cuenta.")
        return False

    self.balance = new_balance
    self.save()
    return True


PREMIUM_PRICES = {
    60: 80,
    90: 100,
}


def purchase_premium(request, account: BankAccount, duration_days: int):
    price = PREMIUM_PRICES[duration_days]

    if account.balance >= price:
        account.duration_days = duration_days
        account.upgraded_at = timezone.now()
        account.balance -= price
        account.save()

        string = "3 meses" if duration_days == 30 else "6 meses"

        messages.success(
            request, f"Has comprado una Cuenta Premium durante {string} por {price} galeones.")

    else:
        messages.error(
            request, "No tienes suficientes galeones para esta cuenta.")


def validate_transaction(request, sender_account, receiver_account, amount):
    if amount < 20:
        messages.error(request, "La transferencia mínima es de 20 galeones.")
        return False

    if sender_account.is_frozen:
        messages.error(request, "La cuenta del remitente está congelada.")
        return False

    if receiver_account.is_frozen:
        messages.error(request, "Alguna de las cuentas está congelada.")
        return False

    total_needed = int(amount * 1.05)
    if sender_account.balance < total_needed:
        messages.error(
            request, "Saldo insuficiente para cubrir: monto + comisión del 5%.")
        return False

    if sender_account.weekly_transactions_left <= 0:
        messages.error(
            request, "El remitente ya realizó su transferencia semanal.")
        return False

    if receiver_account.weekly_transactions_left <= 0:
        messages.error(
            request, "El receptor ya recibió su transferencia semanal.")
        return False

    new_balance = receiver_account.balance + amount
    if receiver_account.current_limit < new_balance:
        messages.error(
            request, "La cantidad de galeones que quieres enviar excede el limite de la cuenta del receptor.")
        return False

    return True


def execute_transaction(request, sender_account, receiver_account, amount, tx_instance):
    if validate_transaction(request, sender_account, receiver_account, amount):

        with db_transaction.atomic():
            sender_account.balance -= int(amount * 1.05)
            sender_account.weekly_transactions_left -= 1
            sender_account.save()

            receiver_account.balance += amount
            receiver_account.weekly_transactions_left -= 1
            receiver_account.save()

            tx_instance.save()

            messages.success(request, "Transferencia exitosa.")
            return tx_instance

    return None
