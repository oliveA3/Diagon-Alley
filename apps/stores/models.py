from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date
from django.templatetags.static import static

User = get_user_model()

STORE_PRODUCT_MAP = {
    0: 'broom',
    1: 'pet',
    2: 'wand',
    3: 'misc',
}


class Store(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()

    STORE_TYPES = [
        ('broom', 'Escobas'),
        ('pet', 'Mascotas'),
        ('wand', 'Varitas'),
        ('misc', 'Miscelaneos'),
    ]
    store_type = models.CharField(max_length=20, choices=STORE_TYPES)

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        return static(f"imgs/stores/{self.id}.jpg")


class Product(models.Model):
    # Fields for all products
    name = models.CharField(max_length=130)
    description = models.TextField()
    price = models.PositiveIntegerField()
    discount = models.DecimalField(default=0.0, decimal_places=2, max_digits=4)

    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name='products'
    )

    PRODUCT_TYPES = [
        ('broom', 'Escoba'),
        ('pet', 'Mascota'),
        ('wand', 'Varita'),
        ('wheezes', 'Sortilegios'),
    ]
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)

    duration_days = models.PositiveIntegerField(blank=True, null=True)

    # For wands and brooms depends on the product, for wheezes = 1
    uses = models.PositiveIntegerField(null=True, blank=True)

    # Just wands and brooms are stackable
    stackable = models.BooleanField(default=False)

    def clean(self):
        errors = {}

        if self.product_type in ['broom', 'wand']:
            if not self.stackable:
                errors['stackable'] = "Las escobas y varitas deben ser stackable."

            if not self.uses or self.uses <= 0:
                errors['uses'] = "Las escobas y varitas deben tener un número de usos mayor a 0."

        elif self.product_type == 'pet':
            if self.stackable:
                errors['stackable'] = "Las mascotas no pueden ser stackable."

            if self.uses is not None:
                errors['uses'] = "Las mascotas no deben tener usos."

        elif self.product_type == 'wheezes':
            if self.uses != 1:
                errors['uses'] = "Los sortilegios deben tener exactamente 1 uso."

            if self.stackable:
                errors['stackable'] = "Los sortilegios no pueden ser stackable."
                
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.store and self.store.store_type:
            self.product_type = self.store.store_type
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class WarehouseItem(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name='warehouse_store')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='warehouse_product')

    stock = models.PositiveIntegerField(blank=True, null=True)
    available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('store_id', 'product_id')

    def __str__(self):
        return f"{self.product.name} from {self.store.name} - ({self.available})"


class InventoryItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='inventory_items')
    store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='inventory_items')

    uses = models.PositiveIntegerField(null=True, blank=True)
    pur_date = models.DateField(auto_now_add=True)

    @property
    def ex_date(self):
        if self.product.duration_days:
            return self.pur_date + timedelta(days=self.product.duration_days)
        return None

    @property
    def is_near_ex(self):
        if not self.ex_date:
            return False
            
        today = timezone.now().date()
        delta_days = (self.ex_date - today).days
        return 0 <= delta_days <= 3  

    def save(self, *args, **kwargs):
        if not self.ex_date and self.product.duration_days:
            self.ex_date = date.today() + timedelta(days=self.product.duration_days)

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
