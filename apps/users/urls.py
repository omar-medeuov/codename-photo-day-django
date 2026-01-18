"""
URL configuration for the users app.

This module defines URL patterns for user authentication endpoints.
"""

from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import LogoutView, UserProfileView, UserRegistrationView

app_name = "users"

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", UserProfileView.as_view(), name="profile"),
]
