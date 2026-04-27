from apps.maintenance import tasks
from django.utils import timezone

def run_maintenance():
    tasks.clear_inventory()
    tasks.reset_stock()
    tasks.freeze_account()

    current_day = timezone.now().day
    if current_day % 3 == 1: 
        tasks.penalize_frozen_accounts()
    
    tasks.delete_frozen_account()
    tasks.downgrade_premium()
    tasks.reset_weekly_transactions()
    tasks.delete_old_transactions()
    tasks.delete_paid_loans()
    tasks.delete_old_purchase_receipts()
    tasks.delete_old_usage_receipts()
    tasks.delete_notifications()