import sqlite3
from datetime import datetime
import os
import django
from neomodel.exceptions import RequiredProperty
from neomodel import db
from sentence_transformers import SentenceTransformer
from book_recommender_app.models import Book, User, Review

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_recommender.settings')
django.setup()

def insert_books(columns, query_results, batch_size):
    books_data = [dict(zip(columns, book)) for book in query_results]

    books_insert_query = '''
    UNWIND $batch AS row
    MERGE (b:Book {book_id: row.book_id})
    SET b.title = row.title,
        b.description = row.description,
        b.authors = row.authors,
        b.image = row.image,
        b.preview_link = row.preview_link,
        b.publisher = row.publisher,
        b.published_date = row.published_date,
        b.published_year = row.published_year,
        b.info_link = row.info_link,
        b.categories = row.categories,
        b.ratings_count = row.ratings_count
    RETURN b
    '''
    for i in range(0, len(books_data), batch_size):
        batch = books_data[i:i+batch_size]  # i have to split the load operation into smaller chunks here
        db.cypher_query(books_insert_query, {"batch": batch})
        print(f"Inserted batch {i // batch_size + 1} with {len(batch)} reviews.")

def insert_users(columns, query_results, batch_size):
    users_data = [dict(zip(columns, user)) for user in query_results]

    users_insert_query = '''
        UNWIND $batch AS row
        MERGE (u:User {user_id: row.user_id})
        SET u.profile_name = row.profile_name
        RETURN u
        '''
    for i in range(0, len(users_data), batch_size):
        batch = users_data[i:i+batch_size]  # i have to split the load operation into smaller chunks here
        db.cypher_query(users_insert_query, {"batch": batch})
        print(f"Inserted batch {i // batch_size + 1} with {len(batch)} reviews.")

def insert_reviews(columns, query_results, batch_size):
    model = SentenceTransformer('all-MiniLM-L6-v2')

    reviews_data = [dict(zip(columns, review)) for review in query_results]

    review_insert_query = '''
    UNWIND $batch AS row
    MERGE (r:Review {review_id: row.review_id})
    SET r.helpfulness_ratio = row.helpfulness_ratio,
        r.review_score = row.review_score,
        r.review_time = row.review_time,
        r.review_summary = row.review_summary,
        r.review_text = row.review_text,
        r.embedding = row.embedding

    WITH r, row
    MATCH (b:Book {book_id: row.book_id})
    MERGE (r)-[:REVIEWS]->(b)

    WITH r, row
    MATCH (u:User {user_id: row.user_id})
    MERGE (u)-[:WROTE_REVIEW]->(r)

    WITH r, row
    MATCH (u:User {user_id: row.user_id})
    MERGE (r)-[:WRITTEN_BY]->(u)

    RETURN r
    '''
    for i in range(0, len(reviews_data), batch_size):
        batch = reviews_data[i:i+batch_size]  # i have to split the load operation into smaller chunks here
        for review in batch:
            review_text = review.get('review_text', '')
            review['embedding'] = model.encode(review_text).tolist()
        db.cypher_query(review_insert_query, {"batch": batch})
        print(f"Inserted batch {i // batch_size + 1} with {len(batch)} reviews.")


conn = sqlite3.connect('books.db')
cursor = conn.cursor()


books_query = '''
Select *
FROM books
LIMIT 25000'''
cursor.execute(books_query)
books = cursor.fetchall()
column_names = [desc[0] for desc in cursor.description]

insert_books(column_names, books, 500)

users_query = '''
SELECT user_id, MIN(profile_name) as profile_name
FROM ratings
WHERE user_id IS NOT NULL
GROUP BY user_id
LIMIT 25000'''
cursor.execute(users_query)
users = cursor.fetchall()
column_names = [desc[0] for desc in cursor.description]

insert_users(column_names, users, 500)

reviews_query = '''
SELECT *
FROM ratings
LIMIT 100000'''

cursor.execute(reviews_query)
reviews = cursor.fetchall()
column_names = [desc[0] for desc in cursor.description]

insert_reviews(column_names, reviews, 200)