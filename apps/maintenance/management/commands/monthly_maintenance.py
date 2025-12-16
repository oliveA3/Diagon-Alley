from django.core.management.base import BaseCommand
from apps.maintenance import tasks

class Command(BaseCommand):
    help = """Rutinas cada 3 dias:
    \nEliminar prestamos pagados.
    """

    def handle(self, *args, **kwargs):
        tasks.delete_paid_loans()

        self.stdout.write(self.style.SUCCESS("✅ Rutinas de mantenimiento ejecutadas"))