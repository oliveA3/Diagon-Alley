from django.utils import timezone
from datetime import timedelta
from .models import Transaction
from django.contrib import messages
from .models import BankAccount
from django.contrib import messages

PREMIUM_PRICES = {
    'premium': 80,
    'premium_pro': 100,
}

def buy_premium(account: BankAccount, new_type: str):
    price = PREMIUM_PRICES[new_type]
    
    if account.balance < price:
        raise ValueError("No tienes suficientes galeones para esta cuenta.")

    account.account_type = new_type
    account.upgraded_at = timezone.now()
    account.balance -= price
    account.save()


# def can_transact(user, direction='send'):
#    now = timezone.now()
#    week_ago = now - timedelta(days=7)
#
#    if direction == 'send':
#        recent = Transaction.objects.filter(
#            sender=user, timestamp__gte=week_ago)
#    else:
#        recent = Transaction.objects.filter(
#            receiver=user, timestamp__gte=week_ago)
#
#    return not recent.exists()
#
#
# def transfer_galleons(sender, receiver, amount):
#    if sender.is_frozen or receiver.is_frozen:
#        return "Una de las cuentas está congelada."
#
#    if sender.balance < amount:
#        return "Saldo insuficiente."
#
#    if not can_transact(sender, 'send'):
#        return "Ya enviaste dinero esta semana."
#
#    if not can_transact(receiver, 'receive'):
#        return "Este usuario ya recibió dinero esta semana."
#
#    # Ejecutar transacción
#    sender.balance -= amount
#    receiver.balance += amount
#    sender.save()
#    receiver.save()
#
#    Transaction.objects.create(sender=sender, receiver=receiver, amount=amount)
#    return f"Transferencia exitosa de {amount} galeones a {receiver.username}."
#
