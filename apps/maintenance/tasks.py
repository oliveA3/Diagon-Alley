from django.utils import timezone
from datetime import timedelta
from apps.stores.models import WarehouseItem, InventoryItem
from apps.bank.models import BankAccount, Loan, Transaction
from apps.utils.models import Notification, UsageReceipt


# Delete expired items on user's inventories (check every day)
def clear_inventory():
    today = timezone.now().date()
    for item in InventoryItem.objects.all():
        if item.ex_date and item.ex_date < today:
            item.delete()

            Notification.objects.create(
                user=item.user,
                message=(
                    f"El artículo {item.product.name} fue eliminado de tu inventario.")
            )


# Reset stock to 10 on WarehouseItems (reset every day)
def reset_stock():
    for item in WarehouseItem.objects.all():
        item.stock = 10
        item.save()


# Freeze account after 30 days of the last purchase (check every day)
def freeze_account():
    today = timezone.now().date()
    for acc in BankAccount.objects.filter(is_frozen=False).exclude(account_type='vip'):
        if acc.last_pur_date and today - acc.last_pur_date >= timedelta(days=30):
            acc.is_frozen = True
            acc.frozen_date = today
            acc.save()

            Notification.objects.create(
                user=acc.user,
                message=("Tu cuenta ha sido congelada por falta de uso, para descongelarla compra un artículo en el Callejón Diagon. Tras 6 meses de inactividad la cuenta será eliminada.")
            )


# Penalize frozen accounts (-5%) (penalize every 3 days)
def penalize_frozen_accounts():
    today = timezone.now().date()
    for acc in BankAccount.objects.filter(is_frozen=True).exclude(pk=1):
        if acc.balance > 0:
            penalty = int(acc.balance * 0.05)
            acc.balance -= penalty
            acc.save()


# Delete frozen accounts after 6 months of being frozen (except pk=1) (check every day)
def delete_frozen_account():
    today = timezone.now().date()
    for acc in BankAccount.objects.filter(is_frozen=True).exclude(pk=1):
        if acc.frozen_date and acc.frozen_date <= today - timedelta(days=180):
            user = acc.user
            acc.delete()
            user.delete()


# Downgrade premium accounts to standard (check every day)
def downgrade_premium():
    today = timezone.now().date()
    expired_premiums = [
        acc for acc in BankAccount.objects.filter(account_type='premium')
        if acc.premium_ex_date and acc.premium_ex_date < today
    ]
    for acc in expired_premiums:
        acc.account_type = 'standard'
        acc.upgraded_at = None
        acc.duration_days = None
        acc.save()
        if acc.current_limit and acc.balance > acc.current_limit:
            acc.balance = acc.current_limit
        acc.save()


# Reset allowed_transactions to 1 after a week from the last transaction (check every day)
def reset_weekly_transactions():
    today = timezone.now().date()
    for acc in BankAccount.objects.all():
        if acc.last_trans_date:
            delta = today - acc.last_trans_date
            if delta.days >= 7:
                acc.weekly_transactions_left = 1
                acc.save()


# Delete transactions 30 days after the creation date (check every day)
def delete_old_transactions():
    cutoff = timezone.now().date() - timedelta(days=30)
    Transaction.objects.filter(created_at__lte=cutoff).delete()


# Delete paid loans after 30 days (every month)
def delete_paid_loans():
    today = timezone.now().date()
    cutoff = today - timedelta(days=30)
    Loan.objects.filter(state='paid', paid_date__lte=cutoff).delete()


# Delete receipts after 30 days
def delete_old_receipts():
    cutoff = timezone.now().date() - timedelta(days=30)
    UsageReceipt.objects.filter(created_at__lte=cutoff).delete()


# Delete notifications after two weeks (check every day)
def delete_notifications():
    cutoff = timezone.now().date() - timedelta(days=14)
    Notification.objects.filter(created_at__lte=cutoff).delete()
