"""Urls for restaurants app"""

from django.urls import path

from . import views

urlpatterns = [
    path('restaurant/', views.restaurant, name='restaurant'),
    path('add_restaurant', views.add_restaurant, name='add_restaurant'),
    path('api/restaurant/step1/', views.restaurant_step1, name='restaurant-step1'),
    path('api/restaurant/step2/', views.restaurant_step2, name='restaurant-step2'),
    path('api/restaurant/step3/', views.restaurant_step3, name='restaurant-step3'),
    # path('api/restaurant/final/', views.restaurant_final, name='restaurant-final'),
    path('api/restaurant-preview/', views.restaurant_preview, name='restaurant-preview'),
    path('api/cuisines/', views.get_cuisines, name='get-cuisines'),
]