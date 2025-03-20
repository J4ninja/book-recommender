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
    category = StringProperty()
    ratings_count = FloatProperty()

    reviews = RelationshipFrom('Review', 'REVIEWS')

class Review(DjangoNode):
    review_id = StringProperty(unique_index = True, required = True)
    book_id = StringProperty(required = True)
    title = StringProperty()
    price = FloatProperty()
    helpfulness_ratio = FloatProperty()
    review_score = FloatProperty()
    review_time = DateTimeProperty()
    review_summary = StringProperty()
    review_text = StringProperty()
    
    reviews = RelationshipTo('Book', 'REVIEWS')
    reviewed_by = RelationshipFrom('User', 'REVIEWED')

class User(DjangoNode):
    user_ID = StringProperty(unique_index = True, required = True)
    profile_name = StringProperty()

    reviewed = RelationshipTo('Review', 'REVIEWED')