from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    id = models.PositiveIntegerField(primary_key=True, unique=True)
    first_name = None
    last_name = None

    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('student', 'Estudiante'),
        ('banker', 'Banquero'),
        ('seller', 'Vendedor'),
    ]
    role = models.CharField(choices=ROLE_CHOICES, default='student')

    username = models.CharField(
        max_length=100,
        unique=True
    )

    full_name = models.CharField(max_length=150, unique=True)

    HOUSE_CHOICES = [
        ('gryffindor', 'Gryffindor'),
        ('hufflepuff', 'Hufflepuff'),
        ('ravenclaw', 'Ravenclaw'),
        ('slytherin', 'Slytherin'),
    ]
    house = models.CharField(null=True, blank=True, choices=HOUSE_CHOICES)


    def __str__(self):
        return f"{self.full_name} ({self.username}) - {self.house}"

        
    def save(self, *args, **kwargs):
        if not self.id:
            used_ids = set(CustomUser.objects.values_list('id', flat=True))
            i = 1
            while i in used_ids:
                i += 1
            self.id = i
        super().save(*args, **kwargs)
