from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.test_data_models, name='search')  # Add this line
]