from django.shortcuts import get_object_or_404, redirect, render
from apps.users.models import CustomUser
from .models import BankAccount, Loan, Transaction
from .services import buy_premium
from django.contrib import messages
from django.db.models import Q
from .services import execute_transaction


def bank_view(request):
    user = request.user
    account = get_object_or_404(BankAccount, user_id=user.id)

    # Premium purchase
    if request.method == 'POST':
        account_type = request.POST.get('account_type')
        buy_premium(account, account_type)
        messages.success(request, "Compra de cuenta premium exitosa.")
        return redirect('bank_view')

    context = {
        'user': user,
        'account': account,
    }

    return render(request, 'bank.html', context)


def transactions_view(request):
    accounts = BankAccount.objects.exclude(user=request.user)

    # Execute transaction
    if request.method == "POST":
        sender = request.user
        receiver_id = request.POST.get("receiver_id")
        receiver = get_object_or_404(CustomUser, id=receiver_id)
        amount = int(request.POST.get("amount"))

        tx = Transaction(sender=sender, receiver=receiver, amount=amount)

        try:
            execute_transaction(sender.bank_account,
                                receiver.bank_account, amount, tx)
            messages.success(request, "✅ Transferencia realizada con éxito.")

        except ValidationError as e:
            messages.error(request, f"❌ Error: {e}")

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


def loans_view(request):
    user = request.user
    accounts = CustomUser.objects.filter(
        ~Q(id=request.user.id),
        is_staff=False,
        is_superuser=False,
        bank_account__is_frozen=False
    )

    # Request loan
    if request.method == 'POST':
        loan_type = int(request.POST.get("loan_type"))

        user_a_id = request.POST.get('user_a')
        codebtor_a = CustomUser.objects.get(id=user_a_id)
        user_b_id = request.POST.get('user_b')
        codebtor_b = CustomUser.objects.get(id=user_b_id)

        amount_requested, amount_due = LOAN_AMOUNTS[loan_type]

        Loan.objects.create(
            user=user,
            codebtor_a=codebtor_a,
            codebtor_b=codebtor_b,
            loan_type=loan_type,
            amount_requested=amount_requested,
            amount_due=amount_due
        )

    context = {
        'user': user,
        'accounts': accounts,
    }

    return render(request, 'loan.html', context)
