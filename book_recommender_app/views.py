import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Book, Review, User
from .recommender import get_book_title_from_review, find_similar_reviews

def index(request):
    '''Home Page view'''
    return render(request, 'index.html')

def test_data_models(request):
    '''Returns all books'''
    return render(request, 'test_data_models.html', {'books': Book.nodes.all()})

def recommendations(request):
    '''renders graph template with user node added and list of user reviews'''
    user_node = User.nodes.get_or_none(user_id = 'A12A08OL0TZY0W')
    user_reviews = user_node.wrote_review.all()

    nodes = []
    relationships = []
    nodes.append({'id': user_node.user_id, 'label': user_node.profile_name, 'type': 'active_user'})
    user_reviews_with_title = []
    for review in user_reviews:
        book_title = get_book_title_from_review(review)
        user_reviews_with_title.append({
            'review_id': review.review_id,
            'review_summary': review.review_summary,
            'book_title': book_title
        })


    return render(request, 'recommendations.html', {'nodes': nodes, 'relationships': relationships, 
                                                    'user_node': user_node, 'user_reviews': user_reviews_with_title})

def get_new_recommendations(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        review_id = data.get('id')

        print(f'Received review_id: {review_id}')

        review = Review.nodes.get_or_none(review_id = review_id)
        new_review_nodes = find_similar_reviews(review)
        return JsonResponse({
                'status': 'success'
            })

@csrf_exempt
def add_node_to_graph(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        review_id = data.get('id')
        review = Review.nodes.get_or_none(review_id = review_id)
        
        if not review:
            return JsonResponse({'status': 'error', 'message': 'Review not found'}, status=404)

        edges = []
        nodes = []

        book = review.reviewed_book.single()
        if book:
            nodes.append({'id': book.book_id, 'label': book.title, 'type': 'book'})
            edges.append({'source': book.book_id, 'target': review_id, 'label': 'REVIEW'})
        user = review.written_by.single()
        if user:
            edges.append({'source': user.user_id, 'target': review_id, 'label': 'WROTE_REVIEW'})

        return JsonResponse({
            'status': 'success',
            'node': {'id': review_id, 'label': review.review_summary, 'type': 'review'},
            'new_nodes': nodes,
            'edges': edges
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)