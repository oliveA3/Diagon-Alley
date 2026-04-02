from django.contrib import admin
from .models import Store, Product, WarehouseItem, InventoryItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "store", "price")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # If new product, create WarehouseItem
        if not change:
            WarehouseItem.objects.create(
                product=obj,
                store=obj.store,
                stock=None,          # puedes inicializar stock en 0 o lo que quieras
                available=True
            )

admin.site.register(Store)
admin.site.register(WarehouseItem)
admin.site.register(InventoryItem)