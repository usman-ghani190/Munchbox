"""Views for restaurants app"""
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from restaurants.form import RestaurantForm
from core.models import Cuisine, Package, RestaurantSubscription
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.models import Restaurant, Package
from .serializers import CuisineSerializer, PackageSerializer, RestaurantStep1Serializer, RestaurantStep2Serializer, RestaurantFinalSerializer, RestaurantStep3Serializer


def restaurant(request):
    """View for restaurant"""
    context = {}
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
    context = {'form': form, 'packages': packages}
    return render(request, 'restaurants/add-restaurant.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restaurant_step1(request):
    serializer = RestaurantStep1Serializer(data=request.data)
    if serializer.is_valid():
        request.session['step1_data'] = serializer.validated_data
        return Response({'message': 'Step 1 data saved', 'next_step': 'select-package'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restaurant_step2(request):
    serializer = RestaurantStep2Serializer(data=request.data)
    if serializer.is_valid():
        request.session['step2_data'] = serializer.validated_data
        packages = Package.objects.all()
        return Response({'message': 'Step 2 data saved', 'packages': PackageSerializer(packages, many=True).data, 'next_step': 'payment'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restaurant_step3(request):
    serializer = RestaurantStep3Serializer(data=request.data)
    if serializer.is_valid():
        request.session['step3_data'] = serializer.validated_data
        return Response({'message': 'Step 3 data saved', 'next_step': 'save-preview'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restaurant_final(request):
    step1_data = request.session.get('step1_data', {})
    step2_data = request.session.get('step2_data', {})
    step3_data = request.session.get('step3_data', {})
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
        del request.session['step1_data']
        del request.session['step2_data']
        del request.session['step3_data']
        return Response({'message': 'Restaurant created', 'restaurant_id': restaurant.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_cuisines(request):
    cuisines = Cuisine.objects.all()
    serializer = CuisineSerializer(cuisines, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)