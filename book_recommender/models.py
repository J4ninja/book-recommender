from django_neomodel import DjangoNode
from neomodel import (StringProperty, DateTimeProperty, UniqueIdProperty, IntegerProperty,
                      FloatProperty, ArrayProperty, RelationshipTo, RelationshipFrom)


class Book(DjangoNode):
    book_ID = StringProperty(unique_index = True, required = True) 
    title = StringProperty()
    description = StringProperty()
    author = StringProperty()
    image = StringProperty()
    preview_link = StringProperty()
    published_date = StringProperty()
    info_link = StringProperty()
    category = StringProperty()

    reviews = RelationshipFrom('Review', 'REVIEWS')

class Review(DjangoNode):
    review_ID = StringProperty(unique_index = True, required = True)
    helpfulness = FloatProperty()
    score = FloatProperty()
    time = DateTimeProperty()
    summary = StringProperty()
    text = StringProperty()
    year = IntegerProperty()

    reviews = RelationshipTo('Book', 'REVIEWS')
    reviewed_by = RelationshipFrom('User', 'REVIEWED')

class User(DjangoNode):
    user_ID = StringProperty(unique_index = True, required = True)
    profile_name = StringProperty()

    reviewed = RelationshipTo('Review', 'REVIEWED')