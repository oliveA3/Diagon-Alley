from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('home/', views.home_view, name='home'),
    path('users/', include('apps.users.urls')),
    path('stores/', include('apps.stores.urls')),
    path('bank/', include('apps.bank.urls')),
    path('dashboard/', include('apps.dashboards.urls')),
    path('faq/', views.faq_view, name='faq'),
    path('terms/', views.terms_view, name='terms'),
]
