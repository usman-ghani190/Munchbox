"""Views for restaurants app"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from restaurants.form import RestaurantForm
from core.models import Package

# Create your views here.

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