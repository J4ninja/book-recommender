from sklearn.metrics.pairwise import cosine_similarity
from django.shortcuts import render
from .models import Book, Review, User

def get_book_title_from_review(review):
    book = review.reviewed_book.get_or_none()
    book_title = book.title if book else 'Unknown Book'
    return book_title

def find_similar_reviews(review):
    all_reviews = Review.nodes.all()
    review_embeddings = [rev.embedding for rev in all_reviews]
    similarities = cosine_similarity([review.embedding], review_embeddings)

    similar_reviews = []
    similar_book_ids = [review.book_id]
    for idx, similarity in enumerate(similarities[0]):
        if review.review_id != all_reviews[idx].review_id and all_reviews[idx].book_id not in similar_book_ids:
            similar_reviews.append({
                'review_id1': review.review_id,
                'review_id2': all_reviews[idx].review_id,
                'similarity': similarity
            })
            similar_book_ids.append(all_reviews[idx].book_id)
    
    similar_reviews = sorted(similar_reviews, key=lambda x: x['similarity'], reverse=True)
    return similar_reviews[:5]
