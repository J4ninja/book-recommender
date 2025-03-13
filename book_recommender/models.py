from django_neomodel import DjangoNode
from neomodel import StringProperty, DateTimeProperty, UniqueIdProperty, FloatProperty, ArrayProperty

class Book(DjangoNode):
    uid = UniqueIdProperty()
    title = StringProperty()
    description = StringProperty()
    authors = ArrayProperty()
    image = StringProperty()
    preview_link = StringProperty()
    published_date = StringProperty()
    info_link = StringProperty()
    categories = ArrayProperty()

class Review(DjangoNode):
    uid = UniqueIdProperty()
    book_ID = StringProperty()
    title = StringProperty()
    user_ID = StringProperty()
    profile_name = StringProperty()
    helpfulness = StringProperty()
    score = FloatProperty()
    time = DateTimeProperty()
    summary = StringProperty()
    text = StringProperty()

