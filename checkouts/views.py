"""Views for checkouts app"""
from django.shortcuts import render

# Create your views here.

def order_details(request):
    """view for order details page"""
    context = {}
    return render(request, 'checkouts/order-details.html', context)

def checkout(request):
    """View for checkout page"""
    context = {}
    return render(request, 'checkouts/checkout.html', context)