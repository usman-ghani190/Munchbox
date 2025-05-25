"""Urls for Homepage"""

from . import views
from django.urls import path

app_name = 'home'

urlpatterns = [
    path('', views.home, name='home'),
    path('explore', views.explore, name='explore'),
    path('landing-page', views.landing_page, name='landing-page'),
    path('about', views.about, name='about'),
]
