from django import forms
from apps.stores.models import Store, Product, WarehouseItem

# Store forms
class StoreCreationForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["name", "description", "store_type"]

class StoreUpdateForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["name", "description", "store_type"]


# Product (WarehouseItem) forms
class ProductCreationForm(forms.ModelForm):
    stock = forms.IntegerField(required=True, min_value=0)
    available = forms.BooleanField(required=False)

    class Meta:
        model = Product
        fields = ["name", "description", "price", "discount", "duration_days", "uses"]

    def save(self, commit=True):
        product = super().save(commit=commit)
        if commit:
            WarehouseItem.objects.create(
                store=product.store,
                product=product,
                stock=self.cleaned_data["stock"],
                available=self.cleaned_data.get("available", False),
            )
        return product


class ProductUpdateForm(forms.ModelForm):
    stock = forms.IntegerField(required=True, min_value=0)
    available = forms.BooleanField(required=False)

    class Meta:
        model = Product
        fields = ["name", "description", "price", "discount", "duration_days", "uses"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        product = self.instance
        if product and product.warehouse_product.exists():
            warehouse = product.warehouse_product.first()
            self.fields["stock"].initial = warehouse.stock
            self.fields["available"].initial = warehouse.available

    def save(self, commit=True):
        product = super().save(commit=commit)
        if commit:
            warehouse = product.warehouse_product.first()
            if warehouse:
                warehouse.stock = self.cleaned_data["stock"]
                warehouse.available = self.cleaned_data["available"]
                warehouse.save()
        return product
