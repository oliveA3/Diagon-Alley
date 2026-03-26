from django.urls import path
from . import views

urlpatterns = [
    path('store/<int:store_id>/', views.store_view, name='store'),
    path("product_owners/<int:product_id>/", views.product_owners_view, name="product_owners"),
    path('gift/<int:product_id>/', views.gift_view, name='gift'),
]