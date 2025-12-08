from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import AdminUserCreationForm

# Creation form for CustomUser on /admin
class CustomUserAdmin(UserAdmin):
    add_form = AdminUserCreationForm
    model = CustomUser


admin.site.register(CustomUser, CustomUserAdmin)
