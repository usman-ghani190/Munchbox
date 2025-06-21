from django.urls import path
from . import views

app_name = 'locations'  # Define the namespace

urlpatterns = [
    path('geo-locator/', views.geo_locator, name='geo_locator'),
]