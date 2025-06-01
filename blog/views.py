"""View for blog app"""
from django.shortcuts import get_object_or_404, redirect, render

from django.db.models import Avg, Count

from core.models import BlogPost, Comment, Restaurant

# Create your views here.

def blogs(request):
    """View for blog page"""
    restaurants = Restaurant.objects.all()[:3].prefetch_related('cuisines', 'reviews')
    blogs = BlogPost.objects.all()[:10]
    popular_posts = BlogPost.objects.order_by('-views')[:4]

    context = {
        'restaurants': restaurants,
        'blogs': blogs,
        'popular_posts': popular_posts,
    }
    return render(request, 'blog/blog.html', context)

def blog_details(request, pk):
    """View for blog details page"""
    blog = get_object_or_404(BlogPost, id=pk)
    blog.views += 1  # Increment views
    blog.save()
    comments = Comment.objects.filter(blog=blog).order_by('-created_at')
    popular_posts = BlogPost.objects.order_by('-views')[:4]
    restaurants = Restaurant.objects.all()[:3].prefetch_related('cuisines', 'reviews')

    context = {
        'blog': blog,
        'comments': comments,
        'popular_posts': popular_posts,
        'restaurants': restaurants,
    }
    return render(request, 'blog/blog_details.html', context)

def comment(request, pk):
    """View to handle blog comment submission"""
    blog = get_object_or_404(BlogPost, id=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        text = request.POST.get('text')
        rating = request.POST.get('rating')

        if request.user.is_authenticated:
            Comment.objects.create(
                blog=blog,
                user=request.user,
                text=text,
                rating=rating
            )
        else:
            Comment.objects.create(
                blog=blog,
                name=name,
                email=email,
                text=text,
                rating=rating
            )
        return redirect('blog:blog-details', pk=pk)
    return redirect('blog:blog-details', pk=pk)