"""Views for restaurants app"""
from django.shortcuts import render

# Create your views here.

def restaurant(request):
    """View for restaurant"""
    context = {}
    return render(request, 'restaurants/restaurant.html', context)

def add_restaurant(request):
    """view for add restaurant page"""
    context = {}
    return render(request, 'restaurants/add-restaurant.html', context)