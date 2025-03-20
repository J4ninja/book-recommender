from django.shortcuts import render
from .models import Book


def index(request):
    '''Home Page view'''
    return render(request, 'index.html')

def test_data_models(request):
    '''Returns all books'''
    return render(request, 'test_data_models.html', {'books': Book.nodes.all()})