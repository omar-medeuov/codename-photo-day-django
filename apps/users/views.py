"""
Views for the users app.

This module contains views for user registration, login, and profile management.
"""

from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserRegistrationSerializer, UserSerializer

User = get_user_model()


@extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        summary="Register a new user",
        description="Create a new user account with username, email, and password.",
    )
)
class UserRegistrationView(generics.CreateAPIView):
    """
    View for user registration.

    Creates a new user and returns JWT tokens.
    """

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        """Create a new user and return JWT tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Authentication"],
    summary="Get current user profile",
    description="Retrieve the authenticated user's profile information.",
)
class UserProfileView(generics.RetrieveAPIView):
    """View for retrieving the authenticated user's profile."""

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        """Return the authenticated user."""
        return self.request.user


@extend_schema(
    tags=["Authentication"],
    summary="Logout user",
    description="Blacklist the refresh token to logout the user.",
)
class LogoutView(APIView):
    """
    View for user logout.

    Blacklists the refresh token to invalidate the session.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """Blacklist the refresh token."""
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"error": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
