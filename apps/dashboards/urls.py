from django.urls import path
from . import views

urlpatterns = [
    path('banker/', views.banker_dashboard_view, name='banker_dashboard'),
    path('transactions/', views.transactions_list_view, name='transactions_list'),
    path('loans/', views.loans_list_view, name='loans_list'),
    #path('storekeeper/', views.bank_view, name='bank_view'),
]
