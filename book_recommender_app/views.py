from django.http import JsonResponse
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

def index(request):
    '''Home Page view'''
    return render(request, 'index.html')

def test_data_models(request):
    '''Returns all books'''
    return render(request, 'test_data_models.html', {'books': Book.nodes.all()})

def recommendations(request):
    user_node = User.nodes.get_or_none(user_id = 'A3OQWLU31BU1Y')
    user_reviews = user_node.wrote_review.all()

    nodes = []
    relationships = []
    nodes.append({'id': user_node.user_id, 'label': user_node.profile_name})

    user_reviews_with_title = []
    for review in user_reviews:
        book_title = get_book_title_from_review(review)
        user_reviews_with_title.append({
            'review_id': review.review_id,
            'review_summary': review.review_summary,
            'book_title': book_title
        })
        nodes.append({'id': review.review_id, 'label': book_title})
        relationships.append({'source': user_node.user_id, 'target': review.review_id})
        similar_reviews = find_similar_reviews(review)
        for review_pair in similar_reviews:
            similar_review = Review.nodes.get_or_none(review_id = review_pair['review_id2'])
            if similar_review:
                similar_book_title = get_book_title_from_review(similar_review)
                nodes.append({'id': similar_review.review_id, 'label': similar_book_title})
                relationships.append({'source': review.review_id, 'target': similar_review.review_id})


    return render(request, 'recommendations.html', {'nodes': nodes, 'relationships': relationships, 'user_node': user_node, 'user_reviews': user_reviews_with_title})

def add_node_to_graph(request):
    review_id = request.GET.get('review_id')
    print(review_id)
    if not review_id:
        return JsonResponse({'error': 'Review ID not provided'}, status=400)
    try:
        review = Review.nodes.get(review_id=review_id)
        node_data = {
            'id': review.review_id,
            'label': review.review_summary 
        }
        return JsonResponse({'node': node_data})
    except Review.DoesNotExist:
        return JsonResponse({'error': 'Review not found'}, status=404)