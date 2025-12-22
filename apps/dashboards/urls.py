from django.urls import path
from . import banker_views, shop_views

urlpatterns = [
    # Banker
    path('banker/', banker_views.banker_dashboard_view, name='banker_dashboard'),
    path('transactions/', banker_views.transactions_list_view, name='transactions_list'),
    path('loans/', banker_views.loans_list_view, name='loans_list'),

    # Shopkeeper
    path('shopkeeper/', shop_views.shop_dashboard_view, name='shopkeeper_dashboard'),
    path("update_store/<int:pk>/", shop_views.update_store_view, name="update_store"),
    path("create_product/<int:store_id>/", shop_views.create_product_view, name="create_product"),
    path("update_product/<int:pk>/", shop_views.update_product_view, name="update_product"),
    path('purchases/', shop_views.purchase_list_view, name='purchase_list'),
    path('usages/', shop_views.usage_list_view, name='usage_list'),
]
