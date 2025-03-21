
import numpy as np
import pandas as pd
from django.shortcuts import render
from .models import Book, Review, User



def add_book(book_id,title, description, authors, image, preview_link, publisher, published_date, published_year, info_link, category, ratings_count):
    new_book = Book(book_id,title, description, authors, image, preview_link, 
                    publisher, published_date, published_year, info_link, category, ratings_count).save()

def add_review(review_id, title, price, helpfulness_ratio, review_score, review_time, review_summary, review_text):
    new_review = new_review = Review(
                    review_id=review_id,
                    title=title,
                    price=price,
                    helpfulness_ratio=helpfulness_ratio,
                    review_score=review_score,
                    review_time=review_time,
                    review_summary=review_summary,
                    review_text=review_text
                ).save()
    add_connections_to_review(new_review)



def add_connections_to_review(new_review):

    user = User.nodes.get_or_none(user_id = new_review.user_id)
    review = Review.nodes.get_or_none(review_id = new_review.review_id)
    if user and review:
        user.wrote_review.connect(review)
        review.written_by.connect(user)


def index(request):
    '''Home Page view'''
    return render(request, 'book_recommender/index.html')

def test_data_models(request):
    '''Returns all books'''
    return render(request, 'book_recommender/test_data_models.html', {'books': Book.nodes.all()})
