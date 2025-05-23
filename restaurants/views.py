from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from restaurants.form import RestaurantForm
from core.models import Cuisine, MenuItem, Package, Promotion, RestaurantSubscription
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.models import Restaurant, Package
from .serializers import CuisineSerializer, PackageSerializer, RestaurantStep1Serializer, RestaurantStep2Serializer, RestaurantFinalSerializer, RestaurantStep3Serializer

@login_required
def restaurant(request, restaurant_id):
    # Fetch the restaurant by its UUID
    restaurant = Restaurant.objects.get(id=restaurant_id)

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
    ).filter(is_first_order=True)  # Assuming first-order promotions for this example

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