from django.shortcuts import get_object_or_404, redirect, render
from apps.users.models import CustomUser
from apps.bank.models import BankAccount, Loan, Transaction
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone

# BANKER DASHBOARD

def is_banker(user):
    return user.is_authenticated and user.role == "banker"


@user_passes_test(is_banker)
def banker_dashboard_view(request):
    accounts = BankAccount.objects.select_related(
        "user").order_by('is_frozen', 'id').filter(user__role="student")

    # Filters
    if request.GET.get("id"):
        accounts = accounts.filter(id=request.GET["id"])
    if request.GET.get("username"):
        accounts = accounts.filter(
            user__username__icontains=request.GET["username"])
    if request.GET.get("full_name"):
        accounts = accounts.filter(
            user__full_name__icontains=request.GET["full_name"])
    if request.GET.get("house"):
        accounts = accounts.filter(user__house__icontains=request.GET["house"])

    # Order
    order = request.GET.get("order")
    if order:
        accounts = accounts.order_by(order)

    if request.method == "POST":
        action = request.POST.get("action")

        
        # Update register
        if action:
            if action.startswith("update_"):
                acc_id = action.split("_")[1]
                account = BankAccount.objects.get(id=acc_id)

                new_balance = int(request.POST.get(f"balance_{acc_id}", account.balance))
                if new_balance <= account.current_limit:
                    account.balance = new_balance
                    account.is_frozen = f"is_frozen_{acc_id}" in request.POST

                    # Premium changes
                    new_type = request.POST.get(f"account_type_{acc_id}", account.account_type)
                    if new_type != account.account_type and new_type != 'standard':
                        account.upgraded_at = timezone.now()
                    account.account_type = new_type

                    # House changes
                    account.user.house = request.POST.get(f"house_{acc_id}", account.user.house)
                    account.user.save()

                    account.save()
                    messages.success(request, f"Cuenta {account.user.username} actualizada.")
                else:
                    messages.error(request, f"La cantidad de galeones excede el limite de la cuenta.")

            # Bulk add
            elif action == "bulk_add":
                ids = request.POST.getlist("selected_accounts")
                amount = int(request.POST.get("amount", 0))
                for acc_id in ids:
                    account = BankAccount.objects.get(id=acc_id)
                    account.balance += amount
                    account.save()
                messages.success(request, f"Se agregaron {amount} galeones a {len(ids)} cuentas.")

            # Bulk delete
            elif action == "bulk_delete":
                ids = request.POST.getlist("selected_accounts")
                BankAccount.objects.filter(id__in=ids).delete()
                messages.success(request, f"Se eliminaron {len(ids)} cuentas.")

        return redirect("banker_dashboard")

    return render(request, "banker/banker_dashboard.html", {"accounts": accounts})


@user_passes_test(is_banker)
def transactions_list_view(request):
    transactions = Transaction.objects.select_related("sender", "receiver").order_by("-created_at")

    context = {
        'transactions': transactions,
    }

    return render(request, 'banker/transactions_list.html', context)


@user_passes_test(is_banker)
def loans_list_view(request):
    loans = Loan.objects.all()

    context = {
        'loans': loans,
    }

    return render(request, 'banker/loans_list.html', context)