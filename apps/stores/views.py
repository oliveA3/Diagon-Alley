from django.shortcuts import redirect, render, get_object_or_404
from urllib.parse import quote
from apps.bank.models import BankAccount
from .models import Store, Product, WarehouseItem, InventoryItem
from .services import purchase_product


def store_view(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    warehouse_items = WarehouseItem.objects.select_related(
        'product').filter(store_id=store_id)
    account = BankAccount.objects.get(user_id=request.user.id)
    discount = InventoryItem.objects.filter(
        user=request.user, product_id=4).exists()

    purchase_message = None

    # Product purchase
    if request.method == 'POST':
        user = request.user
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        purchase_message = purchase_product(
            request, user, account, product, store, discount)

    context = {
        'store': store,
        'warehouse_items': warehouse_items,
        'discount': discount,
        'purchase_message': purchase_message,
    }

    return render(request, 'stores/store.html', context)
