from django.shortcuts import redirect, render, get_object_or_404
from urllib.parse import quote
from apps.bank.models import BankAccount
from .models import Store, Product, WarehouseItem, InventoryItem
from .services import purchase_product
from django.db.models import Max
from datetime import datetime


def store_view(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    warehouse_items = WarehouseItem.objects.select_related(
        'product').filter(store_id=store_id)
    account = BankAccount.objects.get(user_id=request.user.id)

    purchase_message = None

    # Product purchase
    if request.method == 'POST':
        user = request.user
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        purchase_message = purchase_product(
            request, user, account, product, store)

    discounts_qs = InventoryItem.objects.filter(
        user=request.user,
        product__discount__isnull=False
    ).exclude(
        product__discount=0
    )

    print(discounts_qs)

    discount = None
    if discounts_qs.exists():
        discount = discounts_qs.aggregate(Max('product__discount'))['product__discount__max']

    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()  # 0 = monday, 6 = sunday

    # Monday to Friday (0-4) from 6am to 11pm
    outside_working_hours = not (0 <= weekday <= 4 and 6 <= hour < 23)

    context = {
        'store': store,
        'warehouse_items': warehouse_items,
        'discount': discount,
        'purchase_message': purchase_message,
        'outside_working_hours': outside_working_hours,
    }

    return render(request, 'store.html', context)
