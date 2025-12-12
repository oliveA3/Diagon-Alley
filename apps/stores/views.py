from django.shortcuts import redirect, render, get_object_or_404
from urllib.parse import quote
from apps.users.models import CustomUser
from apps.bank.models import BankAccount
from .models import Store, Product, WarehouseItem, InventoryItem
from .services import purchase_product, get_discount, gift_product
from apps.utils import utils


def store_view(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    warehouse_items = WarehouseItem.objects.select_related(
        'product').filter(store_id=store_id)
    account = BankAccount.objects.get(user_id=request.user.id)

    purchase_message = None

    discount = get_discount(request.user)

    # Product purchase
    if request.method == 'POST':
        user = request.user
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        purchase_message = purchase_product(
            request, user, account, product, discount, store)

    working_hours = utils.working_hours()

    context = {
        'store': store,
        'warehouse_items': warehouse_items,
        'discount': discount,
        'purchase_message': purchase_message,
        'working_hours': working_hours,
    }

    return render(request, 'store.html', context)

def gift_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    accounts = BankAccount.objects.exclude(user=request.user)
    store = product.store_id

    discount = get_discount(request.user)

    if request.method == "POST":
        receiver_id = request.POST.get("receiver_id")
        receiver = get_object_or_404(CustomUser, id=receiver_id)

        sender = get_object_or_404(BankAccount, user=request.user.id)

        gift_product(request, sender, receiver, product_id, discount, store)

    context = {
        'product': product,
        'accounts' : accounts,
    }

    return render(request, "gift.html", context)