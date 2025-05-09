from django.shortcuts import render
from django.contrib.auth import login as auth_login
import rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.authtoken.models import Token
from accounts.serializers import RegisterSerializer, LoginSerializer
from django.contrib.auth import logout
import logging


logger = logging.getLogger(__name__)

# Template Views
def login(request):
    """View for login page"""
    context = {}
    return render(request, 'accounts/login.html', context)

def register(request):
    """View for register page"""
    context = {}
    return render(request, 'accounts/register.html', context)

# API Views
class RegisterAPIView(APIView):
    def post(self, request):
        logger.debug(f"Received registration request: {request.data}")
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get(user=user)
            keep_signed_in = serializer.validated_data.get('keep_signed_in', False)
            if keep_signed_in:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # Browser close
            logger.info(f"User registered: {user.email}")
            return Response({
                'token': token.key,
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }, status=status.HTTP_201_CREATED)
        logger.error(f"Registration failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    def post(self, request):
        try:
            logger.debug(f"Received login request: {request.data}")
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                auth_login(request, user)  # Ensure the user is logged into the session
                token, created = Token.objects.get_or_create(user=user)
                keep_signed_in = serializer.validated_data.get('keep_signed_in', False)
                if keep_signed_in:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Browser close
                logger.info(f"User logged in: {user.email}")
                next_url = request.GET.get('next', '/')  # Get next URL
                return Response({
                    'token': token.key,
                    'redirect': next_url,  # Include next URL in response
                    'user': {
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                }, status=status.HTTP_200_OK)
            logger.error(f"Login failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Throttled:
            return Response({'detail': 'Too many login attempts. Please try again later.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

class LogoutAPIView(APIView):
    authentication_classes = [rest_framework.authentication.TokenAuthentication]
    permission_classes = [rest_framework.permissions.IsAuthenticated]

    def post(self, request):
        logger.debug(f"POST logout request for user: {request.user.email}")
        try:
            request.user.auth_token.delete()
            logout(request)
            logger.info(f"User logged out: {request.user.email}")
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return Response({"error": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        logger.warning(f"GET logout request for user: {request.user.email} (POST recommended)")
        try:
            request.user.auth_token.delete()
            logout(request)
            logger.info(f"User logged out: {request.user.email}")
            return Response({"message": "Successfully logged out (use POST for security)."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return Response({"error": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST)