from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('house_stats/', views.house_stats_view, name='house_stats'),
    path('edit_profile/', views.edit_profile_view, name='edit_profile'),
    path('update_password/', views.update_password_view, name='update_password'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]
