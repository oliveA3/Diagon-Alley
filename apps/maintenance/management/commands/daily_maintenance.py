from django.core.management.base import BaseCommand
from apps.maintenance import tasks

class Command(BaseCommand):
    help = """Rutinas diarias:
    \nLimpiar el inventario.
    \nResetear el stock.
    \nCongelar cuentas con un mes de desuso.
    \nEliminar cuentas congeladas despues de 6 meses.
    \nExpirar cuentas premium y volver a standard.
    \nResetear las transacciones semanales.
    \nBorrar notificaciones despues de un mes.
    \nBorrar transacciones despues de un mes.
    """

    def handle(self, *args, **kwargs):
        tasks.clear_inventory()
        tasks.reset_stock()
        tasks.freeze_account()
        tasks.delete_frozen_account()
        tasks.downgrade_premium()
        tasks.reset_weekly_transactions()
        tasks.delete_notifications()
        tasks.delete_old_transactions()

        self.stdout.write(self.style.SUCCESS("✅ Rutinas de mantenimiento ejecutadas"))
