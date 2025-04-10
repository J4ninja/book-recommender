from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import Review
from neomodel import db

def get_book_title_from_review(review):
    '''gets book title from a review object'''
    book = review.reviewed_book.get_or_none()
    book_title = book.title if book else 'Unknown Title'
    return book_title

def get_reviews_to_compare(review):
    '''gets all reviews for a book, excluding the passed in review'''

    query = '''
    MATCH (r:Review)-[:REVIEWS]->(b:Book)<-[:REVIEWS]-(other:Review)
    WHERE r.review_id = $review_id AND r <> other
    RETURN other
    '''

    results, _ = db.cypher_query(query, {'review_id': review.review_id})

    return [Review.inflate(row[0]) for row in results]

def find_similar_reviews(review):
    '''given a review, returns a list object, with each element containing a list of [similar_review, reviewer]'''
    all_reviews = get_reviews_to_compare(review)
    review_embedding = np.array(review.embedding)
    all_embeddings = [np.array(rev.embedding) for rev in all_reviews]
    cosine_sim = cosine_similarity([review_embedding], all_embeddings)[0]
    sorted_indices = np.argsort(cosine_sim)[::-1]
    unique_users = []
    most_similar_reviews = []
    for i in sorted_indices:
        similar_review = all_reviews[i]
        reviewer = similar_review.written_by.single()
        if reviewer not in unique_users:  
            unique_users.append(similar_review.written_by.single())
            most_similar_reviews.append([similar_review, reviewer])
        if len(most_similar_reviews) == 5:
            break
    print(most_similar_reviews)
    return most_similar_reviews

def get_highest_rated_reviews(user):
    '''given a user node, returns the 5 highest rated reviews written by that user'''
    query = '''
    MATCH (u:User)-[:WROTE_REVIEW]->(r:Review)
    WHERE u.user_id = $user_id
    ORDER BY r.review_score DESC
    RETURN r
    LIMIT 5
    '''

    results, _ = db.cypher_query(query, {'user_id': user.user_id})

    # Extract review nodes from query results
    return [Review.inflate(row[0]) for row in results]