"""Models for Munchbox"""

from django.db import models
from django.db.models import Avg, Count
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.utils.text import slugify

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

    @property
    def average_rating(self):
        return self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def latest_reviewer(self):
        latest_review = self.reviews.order_by('-created_at').first()
        return latest_review.user if latest_review else None

    @property
    def latest_review(self):
        latest_review = self.reviews.order_by('-created_at').first()
        return latest_review.comment if latest_review else None

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

# BlogPost Model (Consolidated)
class BlogPost(models.Model):
    id = models.AutoField(primary_key=True)  # Using AutoField for simplicity
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='blog_posts')
    date = models.DateTimeField(auto_now_add=True)
    excerpt = models.TextField(blank=True, null=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)  # Added from second definition
    slug = models.SlugField(unique=True, max_length=200, blank=True)  # Added from second definition
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date']

# Comment Model
class Comment(models.Model):
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    text = models.TextField()
    rating = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])  # Added validators
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f"Comment by {self.name or self.user.username} on {self.blog.title}"

# Slider Item
class SliderItem(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='slider_images/', blank=True, null=True)
    button_url = models.CharField(max_length=200, blank=True, help_text="URL for the button (e.g., /restaurants/restaurant_list/)")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

# About Us Section
class AboutUsSection(models.Model):
    title = models.CharField(max_length=200)
    description_1 = models.TextField()
    description_2 = models.TextField(blank=True)
    image_1 = models.ImageField(upload_to='about_images/', blank=True, null=True)
    image_2 = models.ImageField(upload_to='about_images/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='about_images/', blank=True, null=True)
    button_text = models.CharField(max_length=50, blank=True)
    button_url = models.CharField(max_length=200, blank=True, help_text="URL for the button (e.g., #)")

    def __str__(self):
        return self.title

# Process Step
class ProcessStep(models.Model):
    step_number = models.PositiveIntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='process_icons/', blank=True, null=True)

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f"{self.step_number}. {self.title}"

# Testimonial
class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.role}"