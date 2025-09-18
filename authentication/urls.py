# authentication/urls.py
from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', views.token_refresh_view, name='token_refresh'),
    
    # Profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.PasswordChangeView.as_view(), name='change_password'),
    
    # Utility endpoints
    path('check-username/', views.check_username, name='check_username'),
    path('check-email/', views.check_email, name='check_email'),

     # Admin endpoints
    path('admin/invalidate-all-tokens/', views.invalidate_all_tokens_view, name='admin_invalidate_all_tokens'),
]
