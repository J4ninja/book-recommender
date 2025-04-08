from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.test_data_models, name='search'), 
    path('recommendations/', views.recommendations, name = 'recommendations'),
    path('add_node_to_graph/', views.add_node_to_graph, name = 'add_node_to_graph'),
    path('get_similar_users/', views.get_similar_users, name = 'get_similar_users'),
    path('get_new_recommendations/', views.get_new_recommendations, name = 'get_new_recommendations'),
]