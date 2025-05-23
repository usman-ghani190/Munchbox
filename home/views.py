"""Views for Homepage"""
from django.shortcuts import render

from core.models import Restaurant

# Create your views here.

def home(request):
    """View for homepage"""

    user_restaurant = Restaurant.objects.filter(user=request.user).first() if request.user.is_authenticated else None
    context = {
        'restaurant': user_restaurant,  # Ensure None is explicit
    }
    return render(request, 'home/homepage.html', context)

def explore(request):
    """View for Explore-deals page"""
    context = {}
    return render(request, 'home/ex-deals.html', context)

def landing_page(request):
    """View for landing page"""
    context = {}
    return render(request, 'home/landing_page.html', context)

def about(request):
    """View for about page"""
    context = {}
    return render(request, 'home/about.html', context)