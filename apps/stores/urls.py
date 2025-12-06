from django.urls import path
from . import views

urlpatterns = [
    path('store/<int:store_id>/', views.store_view, name='store_view'),
]
