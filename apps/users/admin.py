from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import AdminUserCreationForm

class CustomUserAdmin(UserAdmin):
    add_form = AdminUserCreationForm
    model = CustomUser

    # Qué columnas mostrar en la lista
    list_display = ("username", "email", "full_name", "house", "role", "is_staff", "is_active")

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
            "fields": ("username", "full_name", "house", "role", "email", "password1", "password2", "is_staff", "is_active"),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
