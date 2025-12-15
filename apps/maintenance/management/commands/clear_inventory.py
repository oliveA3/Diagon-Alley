from django.core.management.base import BaseCommand
from apps.maintenance import tasks

class Command(BaseCommand):
    help = "Elimina productos expirados de los inventarios"

    def handle(self, *args, **kwargs):
        count = tasks.clear_inventory()
        self.stdout.write(self.style.SUCCESS(f"Se eliminaron {count} productos expirados"))
