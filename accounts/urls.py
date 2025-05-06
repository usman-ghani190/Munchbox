"""Urls for Accounts app"""

from django.urls import path


from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('api/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/logout/', views.LogoutAPIView.as_view(), name='api_logout'),
]
