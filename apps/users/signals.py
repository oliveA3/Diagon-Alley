from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from apps.utils.models import Notification
from apps.bank.models import BankAccount

@receiver(user_logged_in)
def check_loyalty_bonus(sender, request, user, **kwargs):
    try:
        account = BankAccount.objects.get(user=user)
    except BankAccount.DoesNotExist:
        return 

    if account.last_pur_date:
        if timezone.now().date() - account.last_pur_date >= timedelta(days=90):
            if account.is_frozen:
                account.balance += 5
                account.save()

                Notification.objects.create(
                    user=user,
                    message="¡Bienvenido de vuelta! Has recibido 5 galeones por tu fidelidad. ¡Úsalos en el Callejón Diagon para descongelar tu cuenta!"
                )

