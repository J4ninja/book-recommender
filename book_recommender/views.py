from django.shortcuts import render
from .models import Book


def index(request):
    print(Book.nodes.all())
    return render(request, 'book_recommender/index.html')

def test_data_models(request):
    """returns all books"""
    return render(request, 'book_recommender/test_data_models.html', {'books': Book.nodes.all()})

