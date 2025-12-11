from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from apps.stores.models import Store


@login_required(login_url='/users/login/')
def home_view(request):
    user = request.user

    if user.role == 'banker':
        return redirect(banker_dashboard)

    #if user.role == 'shopkeeper':
    #    return redirect(shopkeeper_dashboard)

    stores = Store.objects.all()
    return render(request, 'home.html', {'stores': stores})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('home/', home_view, name='home'),
    path('users/', include('apps.users.urls')),
    path('stores/', include('apps.stores.urls')),
    path('bank/', include('apps.bank.urls')),
]
