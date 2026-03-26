from django.contrib import admin
from .models import Store, Product, WarehouseItem, InventoryItem

admin.site.register(Store)
admin.site.register(Product)
admin.site.register(WarehouseItem)
admin.site.register(InventoryItem)
