from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('home/', views.home_view, name='home'),
    path('users/', include('apps.users.urls')),
    path('stores/', include('apps.stores.urls')),
    path('bank/', include('apps.bank.urls')),
    path('dashboard/', include('apps.dashboards.urls')),
]
