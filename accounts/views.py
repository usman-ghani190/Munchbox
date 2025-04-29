"""views for accounts"""
from django.shortcuts import render

# Create your views here.

def login(request):
    """view for login page"""
    context =  {}

    return render(request, 'accounts/login.html', context)

def register(request):
    """view for register page"""
    context =  {}

    return render(request, 'accounts/register.html', context)