"""Urls for checkouts app"""


from django.urls import path

from . import views

urlpatterns = [
    path('order-details/', views.order_details, name='order_details'),
    path('checkout', views.checkout, name='checkout')
]
