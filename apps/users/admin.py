from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import AdminUserCreationForm


class CustomUserAdmin(UserAdmin):
    add_form = AdminUserCreationForm
    model = CustomUser


admin.site.register(CustomUser, CustomUserAdmin)
