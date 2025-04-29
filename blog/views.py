"""View for blog app"""
from django.shortcuts import render

# Create your views here.

def blogs(request):
    """view for blog page"""
    context = {}
    return render(request, 'blog/blog.html', context)

def blog_details(request):
    """view for blog dtails page"""
    context = {}
    return render(request, 'blog/blog-details.html', context)