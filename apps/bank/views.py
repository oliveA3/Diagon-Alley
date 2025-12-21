from django.shortcuts import get_object_or_404, redirect, render
from apps.users.models import CustomUser
from .models import BankAccount, Loan, Transaction
from .services import purchase_premium, execute_transaction
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import ValidationError
from apps.utils import utils
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django.contrib.auth.decorators import login_required

@login_required
def bank_view(request):
    user = request.user
    account = get_object_or_404(BankAccount, user_id=user.id)
    pending_loans = Loan.objects.filter(
        user=user, approved=True, state='pending').exists()

    # Premium purchase
    if request.method == 'POST':
        duration_days = int(request.POST.get('account_duration'))
        purchase_premium(request, account, duration_days)
        return redirect('bank_view')

    working_hours = utils.working_hours()

    context = {
        'user': user,
        'account': account,
        'working_hours': working_hours,
        'pending_loans': pending_loans,
    }

    return render(request, 'bank.html', context)

@login_required
def transactions_view(request):
    accounts = BankAccount.objects.exclude(user=request.user)

    # Execute transaction
    if request.method == "POST":
        sender = request.user
        receiver_id = request.POST.get("receiver_id")
        receiver = get_object_or_404(CustomUser, id=receiver_id)
        amount = int(request.POST.get("amount"))

        tx = Transaction(sender=sender, receiver=receiver, amount=amount)

        execute_transaction(request, sender.bank_account,
                            receiver.bank_account, amount, tx)

        return redirect("transactions")

    context = {
        'accounts': accounts,
    }

    return render(request, 'transactions.html', context)


LOAN_AMOUNTS = {
    0: (25, 30),
    1: (50, 60),
    2: (100, 120),
}

@login_required
def loans_view(request):
    user = request.user
    users = CustomUser.objects.order_by('full_name').filter(
        ~Q(id=user.id),
        is_staff=False,
        is_superuser=False,
        bank_account__is_frozen=False,
        role='student',
    )

    if request.method == 'POST':
        loan_type = int(request.POST.get("loan_type"))
        user_a_id = request.POST.get('codebtor_a')
        user_b_id = request.POST.get('codebtor_b')

        amount_requested, amount_due = LOAN_AMOUNTS[loan_type]

        # Validations
        if not user_a_id and not user_b_id:
            messages.error(request, "Debe seleccionar al menos un codeudor.")
        else:
            balance_total = 0
            codebtor_a = None
            codebtor_b = None

            # Available balance
            if user_a_id:
                codebtor_a = CustomUser.objects.get(id=user_a_id)
                balance_total += codebtor_a.bank_account.balance

            if user_b_id:
                codebtor_b = CustomUser.objects.get(id=user_b_id)
                balance_total += codebtor_b.bank_account.balance

            if balance_total < amount_due:
                messages.error(
                    request, "Los codeudores no tienen suficientes galeones para respaldar este préstamo."
                )
            else:
                loan = Loan.objects.create(
                    user=user,
                    codebtor_a=codebtor_a,
                    codebtor_b=codebtor_b,
                    loan_type=loan_type,
                    amount_requested=amount_requested,
                    amount_due=amount_due,
                )
                
                messages.success(
                    request, "Préstamo solicitado. Espera aprobación del banquero.")

    context = {
        'user': user,
        'users': users,
    }
    return render(request, 'loans.html', context)


def pending_loans_view(request):
    user = request.user
    pending_loans = Loan.objects.filter(
        user=user, approved=True, state='pending')

    if request.method == "POST":
        loan_id = request.POST.get("loan_id")
        loan = Loan.objects.get(id=loan_id, user=user,
                                approved=True, state='pending')
        account = user.bank_account

        if account.balance >= loan.amount_due:
            account.balance -= loan.amount_due
            account.save()

            loan.state = 'paid'
            loan.save()
            messages.success(request, f"Has pagado tu préstamo.")

        else:
            messages.error(
                request, "No tienes suficientes galeones para pagar este préstamo.")

    context = {
        "user": user,
        "pending_loans": pending_loans,
    }
    return render(request, "pending_loans.html", context)
