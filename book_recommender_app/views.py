import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Book, Review, User
from .recommender import get_book_title_from_review, find_similar_reviews, get_highest_rated_reviews

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

@csrf_exempt
def add_node_to_graph(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        review_id = data.get('id')
        review = Review.nodes.get_or_none(review_id = review_id)
        
        if not review:
            return JsonResponse({'status': 'error', 'message': 'Review not found'}, status=404)

        edges = []

        user = review.written_by.single()
        if user:
            edges.append({'source': user.user_id, 'target': review_id, 'label': 'WROTE_REVIEW'})

        return JsonResponse({
            'status': 'success',
            'node': {'id': review_id, 'label': get_book_title_from_review(review), 'type': 'review'},
            'edges': edges
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def get_similar_users(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        review_id = data.get('id')

        print(f'Received review_id: {review_id}')

        review = Review.nodes.get_or_none(review_id = review_id)
        similar_reviews = find_similar_reviews(review)

        if not similar_reviews:
            return JsonResponse({'status': 'error', 'message': 'No Similar Reviews Found'}, status=404)

        nodes = []
        edges = []

        if similar_reviews:
            for similar_review_reviewer in similar_reviews:
                similar_review = similar_review_reviewer[0]
                similar_user = similar_review_reviewer[1]
                if similar_review and similar_user:
                    nodes.append({'id': similar_user.user_id, 'label': similar_user.profile_name, 'type': 'user'})
                    edges.append({'source': review_id, 'target': similar_user.user_id, 'label': 'REVIEWED'})

        return JsonResponse({
                'status': 'success',
                'nodes': nodes,
                'edges': edges
            })

def get_new_recommendations(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('id')

        user = User.nodes.get_or_none(user_id = user_id)

        if not user:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        
        nodes = []
        edges = []

        user_reviews = get_highest_rated_reviews(user)

        for user_review in user_reviews:
            if user_review:
                nodes.append({'id': user_review.review_id, 'label': get_book_title_from_review(user_review), 'type': 'review'})
                edges.append({'source': user_review.review_id, 'target': user.user_id, 'label': 'REVIEWED'})

        return JsonResponse({
                'status': 'success',
                'nodes': nodes,
                'edges': edges
            })