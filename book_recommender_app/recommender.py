from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import Book, Review, User
from neomodel import db

def get_book_title_from_review(review):
    '''gets book title from a review object'''
    book = review.reviewed_book.get_or_none()
    book_title = book.title if book else 'Unknown Title'
    return book_title

def get_reviews_to_compare(review):
    '''Gets all reviews written by authors who reviewed the same book as the given review.'''

    query = '''
    MATCH (r:Review)-[:REVIEWS]->(b:Book)<-[:REVIEWS]-(other:Review)
    WHERE r.review_id = $review_id AND r <> other
    MATCH (other)-[:WRITTEN_BY]->(u:User)
    MATCH (u)-[:WROTE_REVIEW]->(wr:Review)
    RETURN DISTINCT wr
    '''

    results, _ = db.cypher_query(query, {'review_id': review.review_id})

    # Convert results to Review objects
    return [review.inflate(row[0]) for row in results]

def find_similar_reviews(review):
    '''finds similar reviews from a review object'''
    all_reviews = get_reviews_to_compare(review)
    review_embedding = np.array(review.embedding)  
    all_embeddings = [np.array(rev.embedding) for rev in all_reviews]
    cosine_sim = cosine_similarity([review_embedding], all_embeddings)[0]
    similar_reviews_indices = np.argsort(cosine_sim)[::-1][:5]
    most_similar_reviews = [all_reviews[i] for i in similar_reviews_indices]
    
    return most_similar_reviews