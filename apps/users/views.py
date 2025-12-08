# views.py
from .forms import StudentLoginForm, StudentRegistrationForm, CustomPasswordChangeForm, EditProfileForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from apps.stores.models import Product, InventoryItem
from apps.bank.models import BankAccount
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

                return render(request, '{user_type}_dashboard.html')

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

    return render(request, 'profile/profile.html', context)


@login_required
def house_stats_view(request):
    user = request.user
    house = user.house

    wands = InventoryItem.objects.filter(product__store_id=3).select_related(
        'user').filter(user__house=user.house).values_list('user__full_name', flat=True).distinct()

    brooms = InventoryItem.objects.filter(product__store_id=1).select_related(
        'user').filter(user__house=user.house).values_list('user__full_name', flat=True).distinct()

    context = {
        'users_with_wands': wands,
        'users_with_brooms': brooms,
    }

    return render(request, 'profile/house_stats.html', context)


@login_required
def edit_profile_view(request):
    user = request.user 

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user) 
        
        if form.is_valid():
            form.save()
            messages.success(request, "¡Tu perfil mágico ha sido actualizado con éxito!")
            
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
