from django import forms
from apps.stores.models import Store, Product, WarehouseItem


class StoreUpdateForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["name", "description", "store_type"]
        labels = {
            "name": "Nombre de la tienda",
            "description": "Descripción",
            "store_type": "Tipo de tienda",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "store_type": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["description"].required = True
        self.fields["store_type"].required = True


class ProductCreationForm(forms.ModelForm):
    stock = forms.IntegerField(
        label="Stock",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    available = forms.BooleanField(
        label="Disponible",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    stackable = forms.BooleanField(
        label="Acumulable",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = Product
        fields = [
            "name", "description", "price", "discount",
            "duration_days", "uses", "stackable", "product_type"
        ]
        labels = {
            "name": "Nombre del producto",
            "description": "Descripción",
            "price": "Precio",
            "discount": "Descuento",
            "duration_days": "Duración (días)",
            "uses": "Usos",
            "stackable": "Acumulable",
            "product_type": "Tipo de producto",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "discount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "duration_days": forms.NumberInput(attrs={"class": "form-control"}),
            "uses": forms.NumberInput(attrs={"class": "form-control"}),
            "product_type": forms.Select(attrs={"class": "form-select"}),
        }

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
    stock = forms.IntegerField(
        label="Stock",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    available = forms.BooleanField(
        label="Disponible",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    stackable = forms.BooleanField(
        label="Acumulable",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = Product
        fields = [
            "name", "description", "price", "discount",
            "duration_days", "uses", "stackable", "product_type"
        ]
        labels = {
            "name": "Nombre del producto",
            "description": "Descripción",
            "price": "Precio",
            "discount": "Descuento",
            "duration_days": "Duración (días)",
            "uses": "Usos",
            "stackable": "Acumulable",
            "product_type": "Tipo de producto",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "discount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "duration_days": forms.NumberInput(attrs={"class": "form-control"}),
            "uses": forms.NumberInput(attrs={"class": "form-control"}),
            "product_type": forms.Select(attrs={"class": "form-select"}),
        }

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
