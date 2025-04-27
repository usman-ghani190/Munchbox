"""Views for Homepage"""
from django.shortcuts import render

# Create your views here.

def home(request):
    """View for homepage"""

    context = {}
    return render(request, 'home/homepage.html', context)