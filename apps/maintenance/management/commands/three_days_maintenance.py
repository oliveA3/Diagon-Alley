from django.core.management.base import BaseCommand
from apps.maintenance import tasks

class Command(BaseCommand):
    help = """Rutinas cada 3 dias:
    \nPenalizar cuentas congeladas (-5%).
    """

    def handle(self, *args, **kwargs):
        tasks.penalize_frozen_accounts()

        self.stdout.write(self.style.SUCCESS("✅ Rutinas de mantenimiento ejecutadas"))