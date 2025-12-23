from .forms import StudentLoginForm, StudentRegistrationForm, CustomPasswordChangeForm, EditProfileForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from apps.stores.models import Product, InventoryItem
from apps.bank.models import BankAccount, Transaction, Loan
from apps.utils.models import Notification
from .models import CustomUser
from apps.utils import utils

User = get_user_model()

# Register view for students


def register_view(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            BankAccount.objects.create(user=user)

            utils.generate_notification(
                user, "¡Bienvenido/a al Callejón Diagon! Da un paseo por nuestras tiendas y guarda tus galeones en el Banco Gringotts.")

            return redirect('login')
    else:
        form = StudentRegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    error_message = None

    if request.method == 'POST':
        form = StudentLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                if user.role == 'student':
                    return redirect('home')

                return redirect(f"{user.role}_dashboard")

            else:
                error_message = "Usuario o contraseña incorrectos."
    else:
        form = StudentLoginForm()

    return render(request, 'login.html', {'form': form, 'error_message': error_message})


# Profile views for students

@login_required
def profile_view(request):
    user = request.user
    bank_account = get_object_or_404(BankAccount, user_id=user.id)
    notifications = Notification.objects.filter(user=user, read=False).exists()

    # Inventory
    wands = InventoryItem.objects.select_related('product').filter(
        user_id=user.id, product__product_type='wand')
    brooms = InventoryItem.objects.select_related('product').filter(
        user_id=user.id, product__product_type='broom')
    pets = InventoryItem.objects.select_related('product').filter(
        user_id=user.id, product__product_type='pet')
    wheezes = InventoryItem.objects.select_related('product').filter(
        user_id=user.id, product__product_type='wheezes')

    # Search by name
    query = request.GET.get("q")
    if query:
        wands = wands.filter(product__name__icontains=query)
        brooms = brooms.filter(product__name__icontains=query)
        pets = pets.filter(product__name__icontains=query)
        wheezes = wheezes.filter(product__name__icontains=query)

    usage_message = None
    pending_loans = Loan.objects.filter(
        user=user, approved=True, state='pending').exists()

    # Use inventory item
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = get_object_or_404(InventoryItem, id=item_id)
        result = item.use()

        receipt = utils.generate_usage_receipt(user, item)
        usage_message = utils.generate_usage_message(receipt)

        if result == 'deleted':
            usage_message += "\n\nEl artículo no tiene más usos, \npor lo que se ha eliminado de su inventario."

    context = {
        'user': user,
        'account': bank_account,
        'notifications': notifications,
        'wands': wands,
        'brooms': brooms,
        'pets': pets,
        'wheezes': wheezes,
        'query': query,
        'usage_message': usage_message,
        'pending_loans': pending_loans,
    }

    return render(request, 'profile/profile.html', context)


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(
        user=request.user).order_by('-created_at')

    context = {
        "notifications": notifications
    }

    if request.method == "POST":
        # Read all
        if "mark_all" in request.POST:
            Notification.objects.filter(
                user=request.user, read=False).update(read=True)

        # Delete all
        if "delete_all" in request.POST:
            Notification.objects.filter(user=request.user).delete()

        return redirect('profile')

    return render(request, 'profile/notifications.html', context)


@login_required
def house_stats_view(request):
    user = request.user
    users_with_wands = CustomUser.objects.filter(
        house=user.house,
        inventory_items__product__product_type='wand'
    ).distinct()

    users_with_brooms = CustomUser.objects.filter(
        house=user.house,
        inventory_items__product__product_type='broom'
    ).distinct()

    return render(request, "profile/house_stats.html", {
        "users_with_wands": users_with_wands,
        "users_with_brooms": users_with_brooms,
        "user": user,
    })


@login_required
def edit_profile_view(request):
    user = request.user

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            messages.success(
                request, "¡Tu perfil mágico ha sido actualizado con éxito!")

            return redirect('profile')

    else:
        form = EditProfileForm(instance=user)

    context = {
        'form': form,
        'user': user,
    }

    return render(request, 'profile/edit_profile.html', context)


@login_required
def update_password_view(request):
    user = request.user

    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=user, data=request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

        return redirect('profile')

    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'profile/update_password.html', {'form': form})
