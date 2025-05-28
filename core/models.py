"""Models for Munchbox"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

# Custom User Model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_restaurant_manager = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

# Cuisine Model
class Cuisine(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Tag Model (e.g., vegetarian, spicy)
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.ImageField(upload_to='tags/icons/', blank=True, null=True)

    def __str__(self):
        return self.name

# Restaurant Model
class Restaurant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True, null=True)
    manager_name = models.CharField(max_length=100, blank=True, null=True)
    manager_phone = models.CharField(max_length=15, blank=True, null=True)
    contact_email = models.EmailField()
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    address = models.TextField(blank=True, null=True)
    delivery_type = models.CharField(
        max_length=20,
        choices=[
            ('delivery', 'Delivery'),
            ('pickup', 'Pickup'),
            ('delivery_and_pickup', 'Delivery & Pickup'),
        ],
        default='delivery_and_pickup'
    )
    cuisines = models.ManyToManyField(Cuisine, related_name='restaurants')
    logo = models.ImageField(upload_to='restaurants/logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='restaurant')

    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"

    def __str__(self):
        return self.name

# Package Model
class Package(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='packages/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (${self.price})"

# Restaurant Subscription
class RestaurantSubscription(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='subscription')
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, related_name='subscriptions')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.package.name}"

# Menu Item Model
class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    calories = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='menu_items/images/', blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='menu_items')
    is_combo = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

# Order Model
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='orders')
    items = models.ManyToManyField(MenuItem, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_type = models.CharField(max_length=20, choices=[
        ('delivery', 'Delivery'),
        ('pickup', 'Pickup'),
    ])
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.restaurant.name}"

# Order Item Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

# Collection 
class Collection(models.Model):
    name = models.CharField(max_length=100)  # e.g., "Top Rated", "New Arrivals"
    filter_type = models.CharField(max_length=50)  # e.g., "top_rated", "recent"
    image = models.ImageField(upload_to='collections/', null=True, blank=True)

    def __str__(self):
        return self.name

# Payment Model
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(
        max_length=20,
        choices=[
            ('credit_card', 'Credit Card'),
            ('paypal', 'PayPal'),
            ('cash', 'Cash'),
            ('gift_card', 'Gift Card'),
            ('amex', 'Amex Express'),
        ]
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.method}"

# Review Model
class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    food_quality = models.BooleanField(default=False)
    delivery_time = models.BooleanField(default=False)
    order_accuracy = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['restaurant', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.restaurant.name} ({self.rating} stars)"

# Promotion Model
class Promotion(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_percentage = models.PositiveIntegerField(blank=True, null=True)
    is_first_order = models.BooleanField(default=False)
    image = models.ImageField(upload_to='promotions/images/', blank=True, null=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title