from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date

User = get_user_model()


class Store(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to='store_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=130)
    description = models.TextField()
    price = models.PositiveIntegerField()

    duration_days = models.PositiveIntegerField(blank=True, null=True)
    uses = models.PositiveIntegerField(null=True, blank=True)
    stackable = models.BooleanField(default=False)

    discount = models.DecimalField(default=0.0, decimal_places=2, max_digits=4)

    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name


class WarehouseItem(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name='warehouse_entries')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='warehouse_entries')

    stock = models.PositiveIntegerField(blank=True, null=True)
    available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('store_id', 'product_id')

    def __str__(self):
        return f"{self.product.name} from {self.store.name} - ({self.available})"


class InventoryItem(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='inventories')
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE, related_name='inventories')
    store = models.ForeignKey(
        'Store', on_delete=models.CASCADE, related_name='inventories')

    uses = models.PositiveIntegerField(null=True, blank=True)
    pur_date = models.DateField(auto_now=True)
    ex_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.ex_date and self.product.duration_days:
            self.ex_date = self.pur_date + \
                timedelta(days=self.product.duration_days)

        super().save(*args, **kwargs)

    def use(self):
        if self.uses > 0:
            self.uses -= 1
            if self.uses == 0:
                self.delete()
                return 'deleted'
            else:
                self.save()
                return 'used'
        return 'empty'

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
