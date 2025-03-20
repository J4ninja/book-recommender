from django.shortcuts import render
from .models import Book


def index(request):
    '''Home Page view'''
    return render(request, 'book_recommender/index.html')

def test_data_models(request):
    '''Returns all books'''
    return render(request, 'book_recommender/test_data_models.html', {'books': Book.nodes.all()})