from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Cuisine, Tag, Restaurant, Package, RestaurantSubscription, MenuItem, Order, OrderItem, Collection, Payment, Review, Promotion

# Register User with custom fields
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'phone_number', 'is_restaurant_manager', 'is_staff')
    list_filter = ('is_restaurant_manager', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'is_restaurant_manager', 'profile_picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number', 'is_restaurant_manager', 'profile_picture')}),
    )

# Register Cuisine
@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Register Tag
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Register Restaurant
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'city', 'delivery_type', 'created_at')
    list_filter = ('delivery_type', 'city', 'country')
    search_fields = ('name', 'contact_email')
    filter_horizontal = ('cuisines',)

# Register Package
@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'created_at')
    search_fields = ('name',)

# Register RestaurantSubscription
@admin.register(RestaurantSubscription)
class RestaurantSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'package', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)

# Register MenuItem
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'price', 'is_combo', 'created_at')
    list_filter = ('restaurant', 'is_combo')
    search_fields = ('name',)
    filter_horizontal = ('tags',)

# Register Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'user', 'total_price', 'delivery_type', 'status', 'created_at')
    list_filter = ('status', 'delivery_type', 'created_at')
    search_fields = ('id', 'restaurant__name', 'user__username')

# Register OrderItem inline with Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

# Add OrderItem inline to Order admin
OrderAdmin.inlines = [OrderItemInline]

# Register Collection
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'filter_type')
    search_fields = ('name', 'filter_type')

# Register Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'method', 'status', 'created_at')
    list_filter = ('method', 'status')

# Register Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('restaurant__name', 'user__username')

# Register Promotion
@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_amount', 'discount_percentage', 'valid_from', 'valid_until')
    list_filter = ('valid_from', 'valid_until')
    search_fields = ('title',)

# Register the custom User model
admin.site.register(User, CustomUserAdmin)