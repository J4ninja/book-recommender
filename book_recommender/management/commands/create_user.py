from django.core.management.base import BaseCommand
from book_recommender.models import User


class Command(BaseCommand):
    '''Helper function to load data into neo4j database'''
    help = 'creates new user node with args user_ID profile_name'
    def add_arguments(self, parser):
        parser.add_argument('user_ID', type=str)
        parser.add_argument('profile_name', type=str)

    def handle(self, *args, **options):
        user_ID = options['user_ID']
        profile_name = options['profile_name']
        new_user = User(user_ID=user_ID,
                        profile_name = profile_name)
        new_user.save()