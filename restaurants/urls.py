"""Urls for restaurants app"""

from django.urls import path

from . import views

urlpatterns = [
    path('restaurant/', views.restaurant, name='restaurant')
]
