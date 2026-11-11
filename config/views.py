from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.shortcuts import render, redirect
from apps.stores.models import Store

@login_required(login_url='/users/login/')
def home_view(request):
    user = request.user

    if user.role == 'banker':
        return redirect('banker_dashboard')

    elif user.role == 'shopkeeper':
        return redirect('shopkeeper_dashboard')

    stores = [
        store for store in Store.objects.all()
        if finders.find(f'imgs/signs/{store.id}.png')
    ]
    return render(request, 'home.html', {'stores': stores})

@login_required(login_url='/users/login/')
def faq_view(request):
    return render(request, 'faq.html')

@login_required(login_url='/users/login/')
def terms_view(request):
    return render(request, 'terms.html')
