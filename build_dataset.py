import sqlite3
import os
import django
from book_recommender.models import Book, User, Review

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_recommender.settings")
django.setup()


def add_book(book_details):
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

def add_user(user_id, profile_name):
    new_user = User(
        user_id = user_id,
        profile_name = profile_name
    ).save()

def add_review(review_details):
    new_review = Review(
            review_id=review_details[0],
            title=review_details[1],
            price=review_details[2],
            helpfulness_ratio=review_details[3],
            review_score=review_details[4],
            review_time=review_details[5],
            review_summary=review_details[6],
            review_text=review_details[7]
        ).save()
    print(new_review.review_id)
    #add_connections_to_review()



def add_connections_to_review(new_review):

    user = User.nodes.get_or_none(user_id = new_review.user_id)
    review = Review.nodes.get_or_none(review_id = new_review.review_id)
    if user and review:
        user.wrote_review.connect(review)
        review.written_by.connect(user)


conn = sqlite3.connect("books.db")
cursor = conn.cursor()


books_query = '''
Select *
FROM books
LIMIT 10'''
cursor.execute(books_query)
books = cursor.fetchall()

for book in books:
    add_book(book)
    book_id = book[0]
    cursor.execute("SELECT * FROM ratings WHERE book_id = ? LIMIT 5", [book_id])
    reviews = cursor.fetchall()
    for review in reviews:
        #add_user()
        add_review(review)

conn.close()