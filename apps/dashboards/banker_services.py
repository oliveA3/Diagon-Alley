from apps.users.models import CustomUser
from apps.stores.models import Product, InventoryItem, WarehouseItem
from apps.bank.models import BankAccount
from apps.utils.utils import get_bonus_if_niffler
from django.db import transaction as db_transaction
from django.contrib import messages
from django.utils import timezone


def bulk_add(request, ids, amount: int):
    for acc_id in ids:
        with db_transaction.atomic():
            account = BankAccount.objects.get(pk=int(acc_id))
            bonus = get_bonus_if_niffler(request, amount, account.user)
            account.balance = account.balance + amount + bonus
            
            if account.is_frozen:
                account.is_frozen = False
            account.save()

            if account.current_limit:
                if account.balance > account.current_limit:
                    account.balance = account.current_limit
            account.save()


def update_account(request, account: BankAccount, new_house: str, new_balance: int, frozen: bool, new_type: str, new_duration: int):
    with db_transaction.atomic():
        account.user.house = new_house
        account.user.save()

        added_amount = new_balance - account.balance
        if added_amount > 0:
            bonus = get_bonus_if_niffler(request, added_amount, account.user)
            if bonus:
                new_balance += bonus

        account.balance = new_balance
        account.save()

        account.is_frozen = not frozen
        account.save()

        if new_type == "premium":
            account.upgraded_at = timezone.now()
            account.duration_days = new_duration
        account.account_type = new_type
        account.save()

        if account.current_limit:
            if new_balance > account.current_limit:
                account.balance = account.current_limit
                account.save()

                messages.error(
                    request, "La cantidad de galeones excede el límite de la cuenta así que pudo haber perdido galeones.")
                return

        messages.success(
            request, f"Cuenta Nº{account.pk} de {account.user.username} actualizada.")
