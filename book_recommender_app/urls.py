from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.test_data_models, name='search'),  # Add this line
    path('recommendations/', views.recommendations, name = 'recommendations'),
    path('add_node_to_graph/', views.add_node_to_graph, name = 'add_node_to_graph'),
]