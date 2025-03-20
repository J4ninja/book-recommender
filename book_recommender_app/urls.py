from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test_data_models', views.test_data_models, name = 'test_data_models')
]