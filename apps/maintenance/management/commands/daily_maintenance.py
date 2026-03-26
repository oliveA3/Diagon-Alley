from django.core.management.base import BaseCommand
from apps.maintenance import tasks
from django.utils import timezone

class Command(BaseCommand):
    help = "Ejecuta rutinas de mantenimiento"

    def handle(self, *args, **kwargs):
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

       

        self.stdout.write(self.style.SUCCESS("✅ Rutinas de mantenimiento ejecutadas"))

