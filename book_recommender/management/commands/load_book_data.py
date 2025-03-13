import os
import csv
from django.core.management.base import BaseCommand
from book_recommender.models import Book


class Command(BaseCommand):
    '''Helper function to load data from csv into neo4j database'''
    help = 'Loads Book Data into Database'

    def handle(self):
        book_import_file = 'books.csv'
        file_path = os.path.join(os.getcwd(), 'data', book_import_file)

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                book = Book(
                    title=row.get('Title', ''),
                    description=row.get('description', ''),
                    authors=[row.get('authors', '')],
                    image=row.get('image', ''),
                    preview_link=row.get('previewLink', ''),
                    publisher=row.get('publisher', ''),
                    published_date=row.get('publishedDate', ''),
                    info_link=row.get('infoLink', ''),
                    categories=[row.get('categories', '')]
                )
                book.save()
