from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import AdminUserCreationForm
from apps.bank.models import BankAccount

class CustomUserAdmin(UserAdmin):
    add_form = AdminUserCreationForm
    model = CustomUser

    # Qué columnas mostrar en la lista
    list_display = ("id", "username", "email", "full_name", "house", "role", "is_staff", "is_active")

    # Campos que se pueden buscar
    search_fields = ("username", "full_name", "email")

    # Orden por defecto
    ordering = ("id",)

    # Configuración de los fieldsets (editar usuario en admin)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Información personal", {"fields": ("full_name", "house", "role", "email")}),
        ("Permisos", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )

    # Configuración de los fieldsets al crear usuario
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("id", "username", "full_name", "house", "role", "email", "password1", "password2", "is_staff", "is_active"),
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            if obj.role == 'student':
                BankAccount.objects.create(user=obj)

admin.site.register(CustomUser, CustomUserAdmin)
