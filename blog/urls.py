"""Urls for blog app"""

from django.urls import path

from . import views

urlpatterns = [
    path('blogs', views.blogs, name='blogs'),
    path('blog-details', views.blog_details, name='blog-details'),
]
