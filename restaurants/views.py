from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Avg
from restaurants.form import RestaurantForm
from core.models import Cuisine, MenuItem, Order, Package, Promotion, RestaurantSubscription
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.models import Restaurant, Package
from .serializers import CuisineSerializer, PackageSerializer, RestaurantStep1Serializer, RestaurantStep2Serializer, RestaurantFinalSerializer, RestaurantStep3Serializer

@login_required
def restaurant(request, restaurant_id):
    # Fetch the restaurant by its UUID, raise 404 if not found
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Fetch related menu items
    menu_items = restaurant.menu_items.all()

    # Fetch all menu items from all restaurants
    all_menu_items = MenuItem.objects.select_related('restaurant').all()

    # Fetch reviews for the restaurant
    reviews = restaurant.reviews.all()
    review_count = reviews.count()
    if review_count > 0:
        avg_rating = sum(review.rating for review in reviews) / review_count
        food_quality_pct = (reviews.filter(food_quality=True).count() / review_count) * 100
        delivery_time_pct = (reviews.filter(delivery_time=True).count() / review_count) * 100
        order_accuracy_pct = (reviews.filter(order_accuracy=True).count() / review_count) * 100
    else:
        avg_rating = 0
        food_quality_pct = 0
        delivery_time_pct = 0
        order_accuracy_pct = 0

    # Fetch active promotions (valid as of now)
    current_time = timezone.now()
    promotions = Promotion.objects.filter(
        valid_from__lte=current_time,
        valid_until__gte=current_time
    ).filter(is_first_order=True)

    # Context data
    context = {
        'restaurant': restaurant,
        'all_menu_items': all_menu_items,
        'menu_items': menu_items,
        'reviews': reviews,
        'review_count': review_count,
        'avg_rating': round(avg_rating, 1),
        'food_quality_pct': round(food_quality_pct),
        'delivery_time_pct': round(delivery_time_pct),
        'order_accuracy_pct': round(order_accuracy_pct),
        'promotions': promotions,
        'user': request.user,
    }

    return render(request, 'restaurants/restaurant.html', context)

@login_required
def add_restaurant(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('restaurant_preview')  # Adjust URL name as needed
    else:
        form = RestaurantForm(user=request.user)
    packages = Package.objects.all()
    cuisines = Cuisine.objects.all()
    print("Cuisines fetched:", list(cuisines))  # Debug log
    context = {'form': form, 'packages': packages, 'cuisines': cuisines}
    return render(request, 'restaurants/add-restaurant.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restaurant_step1(request):
    serializer = RestaurantStep1Serializer(data=request.data)
    if serializer.is_valid():
        request.session['step1_data'] = serializer.validated_data
        return Response({'message': 'Step 1 data saved', 'next_step': 'select-package'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def restaurant_step2(request):
    if request.method == 'POST':
        serializer = RestaurantStep2Serializer(data=request.data)
        if serializer.is_valid():
            request.session['step2_data'] = {'package': serializer.validated_data['package'].pk}
            return Response({'message': 'Step 2 data saved', 'next_step': 'payment'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        packages = Package.objects.all()
        return Response({'packages': PackageSerializer(packages, many=True).data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restaurant_step3(request):
    serializer = RestaurantStep3Serializer(data=request.data)
    if serializer.is_valid():
        request.session['step3_data'] = serializer.validated_data
        # Combine all data and save
        step1_data = request.session.get('step1_data', {})
        step2_data = request.session.get('step2_data', {})
        all_data = {**step1_data, **step2_data}

        serializer = RestaurantFinalSerializer(data=all_data, context={'request': request})
        if serializer.is_valid():
            restaurant = serializer.save()
            # Create RestaurantSubscription
            package = Package.objects.get(id=step2_data['package'])
            end_date = datetime.now() + timedelta(days=package.duration_days)
            RestaurantSubscription.objects.create(
                restaurant=restaurant,
                package=package,
                end_date=end_date
            )
            # Clear session data
            request.session.pop('step1_data', None)
            request.session.pop('step2_data', None)
            request.session.pop('step3_data', None)
            return Response({
                'message': 'Restaurant created',
                'restaurant_id': str(restaurant.id),
                'next_step': 'preview'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def restaurant_preview(request):
    # Fetch the latest restaurant created by the user for preview
    restaurant = Restaurant.objects.filter(user=request.user).order_by('-created_at').first()
    if restaurant:
        preview_html = f"""
        <h3>Restaurant Created Successfully!</h3>
        <p><strong>Name:</strong> {restaurant.name}</p>
        <p><strong>Contact Email:</strong> {restaurant.contact_email}</p>
        <p><strong>Location:</strong> {restaurant.address}, {restaurant.city}, {restaurant.state}, {restaurant.country}</p>
        <p><strong>Delivery Type:</strong> {restaurant.get_delivery_type_display()}</p>
        <p><strong>Cuisines:</strong> {', '.join(cuisine.name for cuisine in restaurant.cuisines.all())}</p>
        """
        return Response({'preview_html': preview_html})
    return Response({'error': 'No restaurant found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_cuisines(request):
    cuisines = Cuisine.objects.all()
    serializer = CuisineSerializer(cuisines, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@login_required
def list_restaurants(request):
    # Fetch all restaurants
    restaurants = Restaurant.objects.all()
    # Fetch the user's own restaurant for base.html
    user_restaurant = Restaurant.objects.filter(user=request.user).first()
    context = {
        'restaurants': restaurants,
        'restaurant': user_restaurant,  # For base.html
    }
    return render(request, 'restaurants/list-restaurants.html', context)

@login_required
def restaurants_by_category(request, category):
    # Assuming category represents a cuisine name for now
    restaurants = Restaurant.objects.filter(cuisines__name=category)
    user_restaurant = Restaurant.objects.filter(user=request.user).first()
    context = {
        'restaurants': restaurants,
        'category': category,
        'restaurant': user_restaurant,  # For base.html
    }
    return render(request, 'restaurants/restaurants_by_category.html', context)

@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    user_restaurant = Restaurant.objects.filter(user=request.user).first()
    context = {
        'order': order,
        'restaurant': user_restaurant,  # For base.html
    }
    return render(request, 'restaurants/order_details.html', context)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    user_restaurant = Restaurant.objects.filter(user=request.user).first()
    context = {
        'orders': orders,
        'restaurant': user_restaurant,
    }
    return render(request, 'restaurants/order_history.html', context)

@login_required
def top_rated_restaurants(request):
    restaurants = Restaurant.objects.annotate(
        avg_rating=Avg('reviews__rating')
    ).filter(avg_rating__isnull=False).order_by('-avg_rating')[:10]
    user_restaurant = Restaurant.objects.filter(user=request.user).first()
    context = {
        'restaurants': restaurants,
        'category': 'Top Rated',
        'restaurant': user_restaurant,
    }
    return render(request, 'restaurants/restaurants_by_category.html', context)

@login_required
def popular_near_you(request):
    user_restaurant = Restaurant.objects.filter(user=request.user).first()
    user_location = (user_restaurant.latitude, user_restaurant.longitude) if user_restaurant and user_restaurant.latitude and user_restaurant.longitude else (40.7128, -74.0060)
    restaurants = Restaurant.objects.annotate(order_count=Count('orders')).exclude(
        latitude__isnull=True, longitude__isnull=True
    )
    nearby = []
    for r in restaurants:
        distance = get_distance(user_location[0], user_location[1], r.latitude, r.longitude)
        if distance <= 10:
            nearby.append((r, distance))
    nearby.sort(key=lambda x: x[0].order_count, reverse=True)
    restaurants = [r[0] for r in nearby[:10]]
    context = {
        'restaurants': restaurants,
        'category': 'Most Popular Near You',
        'restaurant': user_restaurant,
    }
    return render(request, 'restaurants/restaurants_by_category.html', context)

def get_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def restaurant_list(request):
    """View to display a list of restaurants."""
    restaurants = Restaurant.objects.all()  # Fetch all restaurants (customize as needed)
    context = {
        'restaurants': restaurants,
    }
    return render(request, 'restaurants/restaurant_list.html', context)