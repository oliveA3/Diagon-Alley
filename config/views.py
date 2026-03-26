from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from apps.stores.models import Store

@login_required(login_url='/users/login/')
def home_view(request):
    user = request.user

    if user.role == 'banker':
        return redirect('banker_dashboard')

    elif user.role == 'shopkeeper':
        return redirect('shopkeeper_dashboard')

    stores = Store.objects.all()
    return render(request, 'home.html', {'stores': stores})

def faq_view(request):
    return render(request, 'faq.html')
