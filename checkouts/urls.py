"""Urls for checkouts app"""


from django.urls import path

from . import views

app_name= 'checkouts'

urlpatterns = [
    path('order-details/', views.order_details, name='order_details'),
    path('checkout/<uuid:restaurant_id>/', views.checkout, name='checkout')
]
