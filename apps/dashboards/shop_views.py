from django.shortcuts import get_object_or_404, redirect, render
from apps.users.models import CustomUser
from apps.stores.models import Store, Product, WarehouseItem, InventoryItem
from apps.bank.models import BankAccount, Loan, Transaction
from apps.utils.models import PurchaseReceipt, UsageReceipt
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from apps.utils.models import Notification
from .banker_services import bulk_add, update_account
from django.contrib.auth.decorators import login_required
from .forms import StoreUpdateForm, ProductCreationForm, ProductUpdateForm

# SHOPKEEPER DASHBOARD


def is_shopkeeper(user):
    return user.is_authenticated and user.role == "shopkeeper"


@user_passes_test(is_shopkeeper)
def shop_dashboard_view(request):
    stores = Store.objects.prefetch_related(
        "products", "warehouse_store").all()

    return render(request, "shopkeeper/shop_dashboard.html", {"stores": stores})


# Dashboard options

@user_passes_test(is_shopkeeper)
def update_store_view(request, pk):
    store = get_object_or_404(Store, pk=pk)
    if request.method == "POST":
        form = StoreUpdateForm(request.POST, instance=store)

        if form.is_valid():
            form.save()
            messages.success(request, "Tienda actualizada correctamente.")
            return redirect("shopkeeper_dashboard")

    else:
        form = StoreUpdateForm(instance=store)

    return render(request, "shopkeeper/forms/store_form.html", {"form": form})


@user_passes_test(is_shopkeeper)
def create_product_view(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    if request.method == "POST":
        form = ProductCreationForm(request.POST)

        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            form.save(commit=True)

            messages.success(request, "Producto creado correctamente.")
            return redirect("shopkeeper_dashboard")

    else:
        form = ProductCreationForm()

    return render(request, "shopkeeper/forms/product_form.html", {"form": form, "store": store})


@login_required
def update_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductUpdateForm(request.POST, instance=product)

        if form.is_valid():
            form.save()

            messages.success(request, "Producto actualizado correctamente.")
            return redirect("shopkeeper_dashboard")

    else:
        form = ProductUpdateForm(instance=product)

    return render(request, "shopkeeper/forms/product_form.html", {"form": form, "product": product})


# Receipts lists

@user_passes_test(is_shopkeeper)
def purchase_list_view(request):
    receipts = PurchaseReceipt.objects.select_related("user", "product").all()

    return render(request, "shopkeeper/purchase_list.html", {
        "receipts": receipts
    })


@user_passes_test(is_shopkeeper)
def usage_list_view(request):
    receipts = UsageReceipt.objects.select_related("user", "product").all()

    return render(request, "shopkeeper/usage_list.html", {
        "receipts": receipts
    })
