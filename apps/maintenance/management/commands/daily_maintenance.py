from django.core.management.base import BaseCommand
from apps.maintenance import maintenance
from django.utils import timezone

class Command(BaseCommand):
    help = "Ejecuta rutinas de mantenimiento"

    def handle(self, *args, **kwargs):
        maintenance.run_maintenance()

        self.stdout.write(self.style.SUCCESS("✅ Rutinas de mantenimiento ejecutadas"))

