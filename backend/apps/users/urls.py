"""
User URL patterns
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', TokenObtainPairView.as_view(), name='token-obtain'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User profile
    path('me/', views.UserProfileView.as_view(), name='user-profile'),
    path('me/stats/', views.user_stats, name='user-stats'),
    path('users/<str:username>/', views.UserDetailView.as_view(), name='user-detail'),
]
