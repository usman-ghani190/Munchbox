"""Munchbox admin"""
from django.contrib import admin

from core.models import Cuisine, MenuItem, Order, OrderItem, Package, Promotion, Restaurant, RestaurantSubscription, Review, Tag, Payment

# Register your models here.
admin.site.register(Cuisine)
admin.site.register(Tag)
admin.site.register(Restaurant)
admin.site.register(Package)
admin.site.register(RestaurantSubscription)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Review)
admin.site.register(Promotion)
