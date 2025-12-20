from apps.users.models import CustomUser
from apps.stores.models import Product, InventoryItem, WarehouseItem
from apps.bank.models import BankAccount
from django.db import transaction as db_transaction
from django.contrib import messages
from django.utils import timezone

def get_amount_if_niffler(request, amount: int, user: CustomUser):
    has_niffler = InventoryItem.objects.filter(
        user=user, product=4).exists()
    new_amount = amount

    if has_niffler:
        fives = new_amount // 5
        bonus = fives * 2
        new_amount += bonus

        if new_amount != amount:
            messages.success(
                request, f"Se otorgaron {new_amount} galeones a la cuenta de {user.username} por tener un escarbato.")

    return new_amount

def bulk_add(ids, amount: int):
    for acc_id in ids:
        with db_transaction.atomic():
            account = BankAccount.objects.get(pk=int(acc_id))
            account.balance += get_amount_if_niffler(
                request, amount, account.user)
            account.save()

            if account.current_limit and account.balance > account.current_limit:
                account.balance = account.current_limit
            account.save()

def update_account(request, account: BankAccount, house: str, new_balance: int, frozen: bool, new_type: str):
    with db_transaction.atomic():
        account.user.house = house

        added_amount = new_balance - account.balance
        new_balance += has_niffler(request, added_amount, account.user)
        account.balance = new_balance
        account.save()
        
        account.is_frozen = not frozen
        account.save()

        if new_type == "premium":
            account.upgraded_at = timezone.now()
        account.account_type = new_type
        account.save()

        if account.current_limit and new_balance <= account.current_limit:
            account.balance = new_balance
            account.save()

            messages.success(
                request, f"Cuenta de {account.user.username} actualizada.")

        elif account.current_limit and new_balance > account.current_limit:
            account.balance = account.current_limit
            account.save()

            messages.error(request, "La cantidad de galeones excede el límite de la cuenta así que pudo haber perdido galeones.")