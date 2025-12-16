from django.core.management.base import BaseCommand
from apps.maintenance import tasks
from django.utils import timezone

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        tasks.clear_inventory()
        tasks.reset_stock()
        tasks.freeze_account()
        tasks.delete_frozen_account()
        tasks.downgrade_premium()
        tasks.reset_weekly_transactions()
        tasks.delete_notifications()
        tasks.delete_old_transactions()
        tasks.delete_paid_loans()

        current_day = timezone.now().day
        
        if current_day % 3 == 1: 
            tasks.penalize_frozen_accounts()

        self.stdout.write(self.style.SUCCESS("✅ Rutinas de mantenimiento ejecutadas"))
