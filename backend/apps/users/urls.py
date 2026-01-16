"""
User URL patterns
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'warnings', views.WarningViewSet, basename='warning')
router.register(r'bans', views.BanViewSet, basename='ban')
router.register(r'moderation-actions', views.ModerationActionViewSet, basename='moderation-action')

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', TokenObtainPairView.as_view(), name='token-obtain'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # User profile
    path('me/', views.UserProfileView.as_view(), name='user-profile'),
    path('me/stats/', views.user_stats, name='user-stats'),
    path('users/<str:username>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # Moderation actions
    path('users/<str:username>/disable/', views.disable_user_account, name='disable-user'),
    path('users/<str:username>/enable/', views.enable_user_account, name='enable-user'),
    
    # Router URLs
    path('', include(router.urls)),
]
