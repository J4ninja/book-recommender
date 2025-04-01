from sklearn.metrics.pairwise import cosine_similarity
from .models import Book, Review, User

def get_book_title_from_review(review):
    '''gets book title from a review object'''
    book = review.reviewed_book.get_or_none()
    book_title = book.title if book else 'Unknown Title'
    return book_title

def get_reviews_to_compare(review):
    '''gets all users that reviewed the same book as the passed in review object'''
    book = review.reviewed_book.get_or_none()
    all_reviews_for_book = [r for r in book.reviews.all() if r.review_id != review.review_id]
    reviewers = [r.written_by for r in all_reviews_for_book]
    print(len(reviewers))
    all_reviews_to_compare = [reviewer.wrote_review for reviewer in reviewers]
    return all_reviews_to_compare

def find_similar_reviews(review):
    '''finds similar reviews from a review object'''
    all_reviews = get_reviews_to_compare(review)
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
