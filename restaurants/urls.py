"""Urls for restaurants app"""

from django.urls import path

from . import views

app_name = 'restaurants'

urlpatterns = [
    path('restaurant/<uuid:restaurant_id>/', views.restaurant, name='restaurant'),
    path('add_restaurant', views.add_restaurant, name='add_restaurant'),
    path('list/', views.list_restaurants, name='list_restaurants'),
    path('category/<str:category>/', views.restaurants_by_category, name='restaurants_by_category'),
    path('order/<uuid:order_id>/', views.order_details, name='order_details'),
    path('orders/', views.order_history, name='order_history'),
    path('top-rated/', views.top_rated_restaurants, name='top_rated_restaurants'),
    path('popular-near-you/', views.popular_near_you, name='popular_near_you'),
    path('api/restaurant/step1/', views.restaurant_step1, name='restaurant-step1'),
    path('api/restaurant/step2/', views.restaurant_step2, name='restaurant-step2'),
    path('api/restaurant/step3/', views.restaurant_step3, name='restaurant-step3'),
    path('api/restaurant-preview/', views.restaurant_preview, name='restaurant-preview'),
    path('api/cuisines/', views.get_cuisines, name='get-cuisines'),
]