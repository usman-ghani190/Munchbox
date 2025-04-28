"""Urls for Homepage"""

from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('explore/', views.explore, name='explore'),
]
