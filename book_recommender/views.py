from django.shortcuts import render
from .models import Book, Review, User

def add_review(review_ID, helpfulness, score, time, summary, text, year, user_ID, book_ID):
    new_review = Review(review_ID, 
                        helpfulness, 
                        score, 
                        time, 
                        summary, 
                        text, 
                        year)
    new_review.save()
    
    user = User.nodes.get(user_ID=user_ID)  
    book = Book.nodes.get(book_ID=book_ID)

    new_review.reviews.connect(book)
    new_review.reviewed_by.connect(user)


def index(request):
    '''Home Page view'''
    return render(request, 'book_recommender/index.html')

def test_data_models(request):
    '''Returns all books'''
    return render(request, 'book_recommender/test_data_models.html', {'books': Book.nodes.all()})