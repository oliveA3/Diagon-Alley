from django.contrib import admin
from .models import BankAccount


class BankAccountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_username',
        'get_full_name',
        'get_user_house',
        'balance',
        'is_frozen',
        'limit',
        'account_type',
    )
    search_fields = ('id', 'user__username', 'user__full_name', 'user__house')
    list_filter = ('user__house', 'is_frozen', 'account_type')
    ordering = ('id', 'user__username', 'user__full_name',)

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Nombre de usuario'

    def get_full_name(self, obj):
        return obj.user.full_name
    get_full_name.short_description = 'Nombre mágico'

    def get_user_house(self, obj):
        return obj.user.house
    get_user_house.short_description = 'Casa'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'banker' and not request.user.is_superuser:
            return qs.filter(user__role='student')
        return qs

    def has_module_permission(self, request):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.role in ['admin', 'banker']
        )

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role == 'banker'

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role == 'banker'

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.role == 'admin'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role in ['admin', 'banker']


admin.site.register(BankAccount, BankAccountAdmin)