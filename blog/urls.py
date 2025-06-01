"""Urls for blog app"""

from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('blogs', views.blogs, name='blogs'),
    path('blog-details', views.blog_details, name='blog-details'),
    path('blog/<uuid:pk>/', views.blog_details, name='blog-details'),
    path('blog/<uuid:pk>/comment/', views.comment, name='comment'),
]
