import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from neomodel import db
from .models import Book, Review, User
from .recommender import get_book_title_from_review, find_similar_reviews, get_highest_rated_reviews

def index(request):
    '''Home Page view'''
    return render(request, 'index.html')

def search(request):
    '''Search and filter books with pagination'''
    # Get filter parameters from request
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    year_filter = request.GET.get('year', '')
    page = request.GET.get('page', 1)
    
    query_params = {}
    cypher_query = "MATCH (b:Book) WHERE 1=1"
    
    if search_query:
        cypher_query += " AND (b.title =~ $search_pattern OR b.authors =~ $search_pattern)"
        query_params['search_pattern'] = f"(?i).*{search_query}.*"
    
    if category_filter:
        cypher_query += " AND b.categories =~ $category_pattern"
        query_params['category_pattern'] = f"(?i).*{category_filter}.*"
    
    if year_filter:
        cypher_query += " AND b.published_year = $year"
        query_params['year'] = int(year_filter)
    
    cypher_query += " RETURN b ORDER BY b.title LIMIT 1000"  # Limit to prevent excessive memory usage
    results, meta = db.cypher_query(cypher_query, query_params)
    
    all_books = [Book.inflate(row[0]) for row in results]
    
    categories_query = "MATCH (b:Book) RETURN DISTINCT b.categories ORDER BY b.categories"
    years_query = "MATCH (b:Book) WHERE b.published_year IS NOT NULL RETURN DISTINCT b.published_year ORDER BY b.published_year DESC"
    
    categories_results, _ = db.cypher_query(categories_query)
    years_results, _ = db.cypher_query(years_query)
    
    categories = [row[0] for row in categories_results if row[0]]
    years = [str(row[0]) for row in years_results if row[0]]
    
    paginator = Paginator(all_books, 10)  # Show 10 books per page
    
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)
    
    page_range = get_page_range(books)
    
    return render(request, 'search.html', {
        'books': books,
        'page_obj': books,
        'page_range': page_range,
        'categories': categories,
        'years': years
    })

def get_page_range(page_obj, delta=2):
    """Create a pagination range with ellipsis for large number of pages"""
    paginator = page_obj.paginator
    page_number = page_obj.number
    num_pages = paginator.num_pages
    
    # Always include first and last page
    if num_pages <= (delta * 2 + 5):
        # If not many pages, show all
        return range(1, num_pages + 1)
    
    page_range = []
    
    page_range.append(1)

    if page_number - delta > 2:
        page_range.append('...')
    
    start_range = max(2, page_number - delta)
    end_range = min(num_pages - 1, page_number + delta)
    page_range.extend(range(start_range, end_range + 1))
    
    if page_number + delta < num_pages - 1:
        page_range.append('...')
    
    if num_pages > 1:
        page_range.append(num_pages)
    
    return page_range

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