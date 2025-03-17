from django_neomodel import DjangoNode
from neomodel import (StringProperty, DateTimeProperty, UniqueIdProperty, 
                      FloatProperty, ArrayProperty, RelationshipTo, RelationshipFrom)


class Book(DjangoNode):
    book_ID = StringProperty(unique_index = True, required = True) #make pk once finalized
    title = StringProperty()
    description = StringProperty()
    authors = ArrayProperty()
    image = StringProperty()
    preview_link = StringProperty()
    published_date = StringProperty()
    info_link = StringProperty()
    categories = ArrayProperty()

    reviews = RelationshipFrom('Review', 'REVIEWS')

class Review(DjangoNode):
    review_ID = StringProperty(unique_index = True, required = True) 
    helpfulness = StringProperty()
    score = FloatProperty()
    time = DateTimeProperty()
    summary = StringProperty()
    text = StringProperty()

    reviews = RelationshipTo('Book', 'REVIEWS')
    reviewed_by = RelationshipFrom('User', 'REVIEWED')

class User(DjangoNode):
    user_ID = StringProperty(unique_index = True, required = True)
    profile_name = StringProperty()

    reviewed = RelationshipTo('Review', 'REVIEWED')