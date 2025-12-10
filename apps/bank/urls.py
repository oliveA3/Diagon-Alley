from django.urls import path
from . import views

urlpatterns = [
    path('', views.bank_view, name='bank_view'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('loans/', views.loans_view, name='loan'),
]
