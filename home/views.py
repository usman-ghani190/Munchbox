"""Views for Homepage"""
from django.utils import timezone
from django.shortcuts import render
from datetime import timedelta

from core.models import AboutUsSection, BlogPost, Collection, Cuisine, Order, ProcessStep, Promotion, Restaurant, SliderItem, Testimonial
from django.db.models import Count, Avg


def home(request):
    """View for homepage"""
    user_restaurant = Restaurant.objects.filter(user=request.user).first() if request.user.is_authenticated else None
    categories = Cuisine.objects.all()
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:4] if request.user.is_authenticated else []

    # Fetch collections (e.g., top 2 for display)
    collections = Collection.objects.all()[:2]

    # Fetch curated restaurants based on collections
    curated_restaurants = []
    for collection in collections:
        if collection.filter_type == 'top_rated':
            restaurants = Restaurant.objects.annotate(
                avg_rating=Avg('reviews__rating')
            ).filter(avg_rating__isnull=False).order_by('-avg_rating')[:6]
        elif collection.filter_type == 'popular_near_you':
            user_location = (user_restaurant.latitude, user_restaurant.longitude) if user_restaurant and user_restaurant.latitude and user_restaurant.longitude else (40.7128, -74.0060)  # Default to Brooklyn
            restaurants = Restaurant.objects.annotate(order_count=Count('orders')).exclude(
                latitude__isnull=True, longitude__isnull=True
            )
            nearby = []
            for r in restaurants:
                distance = get_distance(user_location[0], user_location[1], r.latitude, r.longitude)
                if distance <= 10:  # Within 10 km
                    nearby.append((r, distance))
            nearby.sort(key=lambda x: x[0].order_count, reverse=True)
            restaurants = [r[0] for r in nearby[:6]]
        else:
            restaurants = Restaurant.objects.annotate(order_count=Count('orders')).order_by('-order_count')[:6]
        curated_restaurants.extend(restaurants)

    # Remove duplicates while preserving order
    curated_restaurants = list(dict.fromkeys(curated_restaurants))[:6]

    context = {
        'restaurant': user_restaurant,
        'categories': categories,
        'recent_orders': recent_orders,
        'collections': collections,
        'curated_restaurants': curated_restaurants,
    }
    return render(request, 'home/homepage.html', context)

def get_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371  # Earth's radius in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def explore(request):
    """View for the explore page"""
    # Annotate all querysets with annotated_review_count
    trending_restaurants = Restaurant.objects.annotate(
        annotated_review_count=Count('reviews')
    ).order_by('-annotated_review_count')[:5]

    featured_restaurants = Restaurant.objects.annotate(
        annotated_review_count=Count('reviews')
    ).order_by('-created_at')[:4]

    fresh_deals = Restaurant.objects.annotate(
        annotated_review_count=Count('reviews')
    ).filter(created_at__gte=timezone.now() - timedelta(days=30))[:5]

    local_deals = Restaurant.objects.annotate(
        annotated_review_count=Count('reviews')
    )[:6]

    context = {
        'featured_restaurants': featured_restaurants,
        'trending_restaurants': trending_restaurants,
        'fresh_deals': fresh_deals,
        'local_deals': local_deals,
    }
    return render(request, 'home/ex-deals.html', context)

def landing_page(request):
    """View for landing page"""
    context = {}
    return render(request, 'home/landing_page.html', context)

def about(request):
    """View for about page"""
    context = {
        'slider_items': SliderItem.objects.filter(is_active=True),
        'about_section': AboutUsSection.objects.first(),  # Assuming one section for now
        'process_steps': ProcessStep.objects.all(),
        'blog_posts': BlogPost.objects.all()[:3],  # Top 3 recent posts
        'testimonials': Testimonial.objects.filter(is_active=True),
    }
    return render(request, 'home/about.html', context)