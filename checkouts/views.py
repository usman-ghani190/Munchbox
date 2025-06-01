from django.shortcuts import render, get_object_or_404
from core.models import Restaurant

def order_details(request):
    """View for order details page"""
    context = {}
    return render(request, 'checkouts/order-details.html', context)

def checkout(request, restaurant_id):
    """View for checkout page"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    context = {
        'restaurant': restaurant,
    }
    return render(request, 'checkouts/checkout.html', context)