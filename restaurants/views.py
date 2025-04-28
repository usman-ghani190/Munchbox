"""Views for restaurants app"""
from django.shortcuts import render

# Create your views here.

def restaurant(request):
    """View for restaurant"""
    context = {}
    return render(request, 'restaurants/restaurant.html', context)