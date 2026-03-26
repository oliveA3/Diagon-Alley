from django.contrib import admin
from .models import BankAccount, Transaction

class BankAccountAdmin(admin.ModelAdmin):
    list_display = ["user_id_display", "user", "balance", "account_type", "is_frozen"]

    def user_id_display(self, obj):
        return obj.user.id
    user_id_display.short_description = "ID Usuario"

    ordering = ["user"]

admin.site.register(BankAccount, BankAccountAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "get_sender", "get_receiver", "amount", "created_at")
    search_fields = ("sender__username", "receiver__username")
    ordering = ("-created_at",)

    def get_sender(self, obj):
        return obj.sender.full_name
    get_sender.short_description = "Remitente"

    def get_receiver(self, obj):
        return obj.receiver.full_name
    get_receiver.short_description = "Receptor"

admin.site.register(Transaction, TransactionAdmin)
