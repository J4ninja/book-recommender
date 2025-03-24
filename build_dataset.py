import sqlite3
import os
import django
from datetime import datetime
from book_recommender.models import Book, User, Review
from neomodel.exceptions import RequiredProperty

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_recommender.settings")
django.setup()


def add_book(book_details):
    '''adds book node from list object'''
    try:
        new_book = Book(
            book_id=book_details[0],
            title=book_details[1],
            description=book_details[2],
            authors=book_details[3],
            image=book_details[4],
            preview_link=book_details[5],
            publisher=book_details[6],
            published_date=book_details[7],
            published_year=book_details[8],
            info_link=book_details[9],
            category=book_details[10],
            ratings_count=book_details[11]
        ).save()
        return new_book
    except RequiredProperty as e:
        print(f'Missing required property : {e}. Node not created')

def add_user(user_id, profile_name):
    '''adds user node from user_id and profile_name'''
    try: 
        new_user = User(
            user_id = user_id,
            profile_name = profile_name
        ).save()
        return new_user
    except RequiredProperty as e:
        print(f'Missing required property : {e}. Node not created')

def add_review(review_details):
    '''adds review node from a list object'''
    try:
        new_review = Review(
                review_id = review_details[0],
                book_id = review_details[1],
                user_id = review_details[4],
                helpfulness_ratio = review_details[6],
                review_score = review_details[7],
                review_time = datetime.strptime(review_details[8], '%Y-%m-%d'),
                review_summary = review_details[9],
                review_text = review_details[10]
            ).save()
        return new_review
    except RequiredProperty as e:
        print(f'Missing required property : {e}. Node not created')

def add_connections_to_review(new_book, new_user, new_review):
    '''takes in a book, user, and review nodes and creates relationships between user <-> review and review <-> book'''
    if new_user and new_review and new_book:
        new_user.wrote_review.connect(new_review)
        new_review.written_by.connect(new_user)
        new_book.reviews.connect(review)
        new_review.reviewed_book.connect(new_book)


conn = sqlite3.connect("books.db")
cursor = conn.cursor()


books_query = '''
Select *
FROM books
LIMIT 100'''
cursor.execute(books_query)
books = cursor.fetchall()

for book in books:
    added_book = add_book(book)
    book_id = book[0]
    cursor.execute("SELECT * FROM ratings WHERE book_id = ? AND user_id IS NOT NULL", [book_id])
    reviews = cursor.fetchall()
    for review in reviews:
        added_user = add_user(user_id = review[4], profile_name = review[5])
        added_review = add_review(review)
        add_connections_to_review(added_book, added_user, added_review)
    print(f'Book ID: {book_id} added')

conn.close()
