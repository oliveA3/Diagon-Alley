from django.shortcuts import get_object_or_404, redirect, render
from apps.users.models import CustomUser
from apps.bank.models import BankAccount, Loan, Transaction
from apps.stores.models import InventoryItem
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from apps.utils.models import Notification
from .banker_services import bulk_add, update_account

# SHOPKEEPER DASHBOARD


def is_shopkeeper(user):
    return user.is_authenticated and user.role == "shopkeeper"


@user_passes_test(is_shopkeeper)
def shop_dashboard_view(request):

    return render(request, "shopkeeper/shop_dashboard.html")


@user_passes_test(is_shopkeeper)
def purchase_list_view(request):

    return render(request, 'shopkeeper/purchase_list.html')


@user_passes_test(is_shopkeeper)
def usage_list_view(request):

    return render(request, 'shopkeeper/usage_list.html')
