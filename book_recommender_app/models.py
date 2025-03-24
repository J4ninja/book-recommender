from django_neomodel import DjangoNode
from neomodel import (StringProperty, DateTimeProperty, UniqueIdProperty, IntegerProperty,
                      FloatProperty, ArrayProperty, RelationshipTo, RelationshipFrom)


class Book(DjangoNode):
    book_id = StringProperty(unique_index = True, required = True) 
    title = StringProperty()
    description = StringProperty()
    authors = StringProperty()
    image = StringProperty()
    preview_link = StringProperty()
    publisher = StringProperty()
    published_date = StringProperty()
    published_year = IntegerProperty()
    info_link = StringProperty()
    categories = StringProperty()
    ratings_count = FloatProperty()

    reviews = RelationshipFrom('Review', 'REVIEWS')

class Review(DjangoNode):
    review_id = StringProperty(unique_index = True, required = True)
    book_id = StringProperty(required = True)
    user_id = StringProperty(required = True)
    helpfulness_ratio = FloatProperty()
    review_score = FloatProperty()
    review_time = DateTimeProperty()
    review_summary = StringProperty()
    review_text = StringProperty()
    embedding = ArrayProperty(FloatProperty())
    
    reviewed_book = RelationshipTo('Book', 'REVIEWS')
    written_by = RelationshipFrom('User', 'WROTE_REVIEW')
    similar_to = RelationshipTo('Review', 'SIMILAR')

class User(DjangoNode):
    user_id = StringProperty(unique_index = True, required = True)
    profile_name = StringProperty()

    wrote_review = RelationshipTo('Review', 'WROTE_REVIEW')