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
    user_node = User.nodes.get_or_none(user_id = 'A101DG7P9E26PW')
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


        #similar_reviews = find_similar_reviews(review)
        #for review_pair in similar_reviews:
        #    similar_review = Review.nodes.get_or_none(review_id = review_pair['review_id2'])
        #    if similar_review:
        #        similar_book_title = get_book_title_from_review(similar_review)
        #        nodes.append({'id': similar_review.review_id, 'label': similar_book_title})
        #        relationships.append({'source': review.review_id, 'target': similar_review.review_id})


    return render(request, 'recommendations.html', {'nodes': nodes, 'relationships': relationships, 
                                                    'user_node': user_node, 'user_reviews': user_reviews_with_title})

@csrf_exempt
def add_node_to_graph(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        review_id = data.get('id')

        print(f'Received review_id: {review_id}')  # Debugging output

        # Try fetching the review
        review = Review.nodes.get_or_none(review_id = review_id)
        print(review)
        
        if not review:
            print(f'Review with ID {review_id} not found!')  # Debugging output
            return JsonResponse({'status': 'error', 'message': 'Review not found'}, status=404)

        edges = []
        nodes = []

        user = review.written_by.single()
        if user:
            nodes.append({'id': user.user_id, 'label': user.profile_name})
            edges.append({'source': user.user_id, 'target': review_id, 'label': 'WROTE_REVIEW'})

        return JsonResponse({
            'status': 'success',
            'node': {'id': review_id, 'label': review.review_summary},
            'new_nodes': nodes,
            'edges': edges
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)