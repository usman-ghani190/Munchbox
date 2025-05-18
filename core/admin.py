"""Munchbox admin"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import Cuisine, MenuItem, Order, OrderItem, Package, Promotion, Restaurant, RestaurantSubscription, Review, Tag, Payment, User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'phone_number', 'is_restaurant_manager', 'profile_picture')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'is_restaurant_manager', 'profile_picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number', 'is_restaurant_manager', 'profile_picture')}),
    )

# Register your models here.
admin.site.register(User, CustomUserAdmin)
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
