from django.urls import path
from . import views

urlpatterns = [
    path('', views.bank_view, name='bank_view'),
    path('transaction/', views.transactions_view, name='transaction'),
    path('loan/', views.loans_view, name='loan'),
]
