# views.py
from .forms import StudentLoginForm, StudentRegistrationForm, CustomPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from apps.stores.models import Product, InventoryItem
from apps.bank.models import BankAccount
from apps.receipts import utils

User = get_user_model()


def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.save()

            BankAccount.objects.create(user=user,
                                       balance=20)

            return redirect('login')
    else:
        form = StudentRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


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
                return redirect('home')

            else:
                error_message = "Usuario o contraseña incorrectos."
    else:
        form = StudentLoginForm()

    return render(request, 'users/login.html', {'form': form, 'error_message': error_message})


@login_required
def profile(request):
    user = request.user

    if user.role != 'student':
        return render(request, 'users/profile.html', {'user': user})

    bank_account = get_object_or_404(BankAccount, user_id=user.id)
    inventory_items = InventoryItem.objects.select_related(
        'product').filter(user_id=user.id)
    usage_message = None

    # Use product
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
        'inventory_items': inventory_items,
        'usage_message': usage_message,
    }

    return render(request, 'users/profile.html', context)


@login_required
def house_stats(request):
    user = request.user
    house = user.house

    if house:
        wands = InventoryItem.objects.filter(product__store_id=3).select_related(
            'user').filter(user__house=user.house).values_list('user__full_name', flat=True).distinct()

        brooms = InventoryItem.objects.filter(product__store_id=1).select_related(
            'user').filter(user__house=user.house).values_list('user__full_name', flat=True).distinct()

        context = {
            'users_with_wands': wands,
            'users_with_brooms': brooms,
        }

        return render(request, 'users/house_stats.html', context)

    return redirect('profile')


@login_required
def edit_profile(request):
    user = request.user
    messages.sucess = []

    if request.method == 'POST':
        new_username = request.POST['username']
        new_full_name = request.POST['full_name']
        errors = []

        # username validation
        if ' ' in new_username:
            raise ValidationError(
                "El nombre de usuario no puede contener espacios.")
        if User.objects.filter(username=new_username).exclude(id=user.id).exists():
            errors.append("Este nombre de usuario ya está en uso.")

        # full_name validation
        if User.objects.filter(full_name=new_full_name).exclude(id=user.id).exists():
            errors.append("Este nombre mágico ya está registrado.")

        if errors:
            return render(request, 'edit_profile.html', {'errors': errors, 'user': user})

        # Update data
        user.username = new_username
        user.full_name = new_full_name
        user.save()
        
        messages.success(request, "Perfil actualizado.")
        return redirect('profile')

    return render(request, 'users/edit_profile.html', {'user': user})


@login_required
def update_password(request):
    user = request.user
    messages.sucess = []
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=user, data=request.POST)
        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Contraseña actualizada.")
            
        return redirect('profile')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'users/update_password.html', {'form': form})
