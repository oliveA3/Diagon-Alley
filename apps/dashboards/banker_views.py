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
from django.contrib.auth.decorators import login_required

# BANKER DASHBOARD

def is_banker(user):
    return user.is_authenticated and user.role == "banker"


@user_passes_test(is_banker)
def banker_dashboard_view(request):
    accounts = BankAccount.objects.select_related("user").filter( user__role="student" ).order_by('is_frozen', 'user__username')

    # Filters
    if request.GET.get("id"):
        accounts = accounts.filter(user=request.GET["id"])
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

        if action:
            # Bulk add
            if action == "bulk_add":
                ids = [i for i in request.POST.getlist(
                    "selected_accounts") if i.strip()]
                amount_raw = request.POST.get("amount", "").strip()

                if not ids:
                    messages.error(
                        request, "Debe seleccionar al menos una cuenta.")

                elif not amount_raw.isdigit():
                    messages.error(
                        request, "Debe ingresar una cantidad válida.")

                else:
                    amount = int(amount_raw)
                    bulk_add(ids, amount)
                    
                    messages.success(
                        request, f"Se agregaron galeones a las cuentas seleccionadas.")

            # Bulk delete
            elif action == "bulk_delete":
                ids = [int(i) for i in request.POST.getlist(
                    "selected_accounts") if i.strip().isdigit()]

                if not ids:
                    messages.error(
                        request, "Debe seleccionar al menos una cuenta para eliminar.")
                else:
                    # Eliminar usuarios asociados
                    CustomUser.objects.filter(pk__in=ids).delete()
                    messages.success(
                        request, f"Se eliminaron {len(ids)} usuarios seleccionados y sus cuentas.")

            # Update register
            elif action.startswith("update_"):
                acc_id = action.split("_")[1]
                account = BankAccount.objects.get(pk=int(acc_id))

                house = request.POST.get(f"house_{acc_id}", account.user.house)
                new_balance = int(request.POST.get(f"balance_{acc_id}"))
                frozen = request.POST.get(f"is_frozen_{acc_id}")
                new_type = request.POST.get(f"account_type_{acc_id}")

                update_account(request, account, house, new_balance, frozen, new_type)

        return redirect("banker_dashboard")

    return render(request, "banker/banker_dashboard.html", {"accounts": accounts})


@user_passes_test(is_banker)
def transactions_list_view(request):
    transactions = Transaction.objects.select_related(
        "sender", "receiver").order_by("-created_at")

    context = {
        'transactions': transactions,
    }

    return render(request, 'banker/transactions_list.html', context)


@user_passes_test(is_banker)
def loans_list_view(request):
    loans_to_approve = Loan.objects.order_by('user').filter(approved=False)
    loans_log = Loan.objects.order_by('user').filter(approved=True)

    if request.method == "POST":
        action = request.POST.get("action")
        loan_id = request.POST.get("loan_id")

        loan = Loan.objects.get(id=loan_id)
        account = get_object_or_404(BankAccount, user=loan.user)

        # Approve loan
        if action == "approve":
            new_balance = account.balance + loan.amount_requested
            if account.current_limit and new_balance <= account.current_limit:
                loan.approved = True
                loan.approved_at = timezone.now()
                loan.save()

                account.balance = new_balance
                account.save()

                due_str = loan.due_date.strftime("%d/%m/%Y")
                Notification.objects.create(
                    user=account.user,
                    message=(
                        f"¡Préstamo aprobado! Ahora cuentas con {loan.amount_requested} galeones, "
                        f"para pagar {loan.amount_due} antes de {due_str}"
                    )
                )

                messages.success(
                    request, f"Préstamo de {loan.user.username} aprobado y balance actualizado.")

            else:
                messages.error(
                    request, f"Este préstamo excede el limite de la cuenta de {loan.user.username}.")

        # Not approve loan
        elif action == "reject":
            loan.delete()
            messages.success(
                request, f"Préstamo de {loan.user.username} rechazado y eliminado.")

        # Mark loan as paid
        elif action == "mark_paid" and loan.state == 'pending':
            today = timezone.now().date()
            loan.paid_date = today
            loan.state = 'paid'
            loan.save()

    context = {
        'loans_to_approve': loans_to_approve,
        'loans_log': loans_log,
    }

    return render(request, 'banker/loans_list.html', context)
