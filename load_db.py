import sqlite3
import os
import django
import numpy as np
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_recommender.settings')
django.setup()



#get cleaned .csvs
books_new = pd.read_csv('data/books_new.csv')
ratings_new = pd.read_csv('data/ratings_new.csv')

## Write the data to a SQLite database ##
# Create connection to SQLite
conn = sqlite3.connect('books.db')
cursor = conn.cursor()

# Drop tables if they exist
cursor.execute('DROP TABLE IF EXISTS ratings')
cursor.execute('DROP TABLE IF EXISTS books')
print('tables dropped')

# Create books table with appropriate data types
create_books_table = '''
CREATE TABLE books (
    book_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    authors TEXT,
    image TEXT,
    preview_link TEXT,
    publisher TEXT,
    published_date TEXT,
    published_year INTEGER,
    info_link TEXT,
    categories TEXT,
    ratings_count FLOAT
)
'''
cursor.execute(create_books_table)

# Create ratings table with appropriate data types and foreign key
create_ratings_table = '''
CREATE TABLE ratings (
    review_id INTEGER PRIMARY KEY,
    book_id TEXT NOT NULL,
    title TEXT,
    price REAL,
    user_id TEXT,
    profile_name TEXT,
    helpfulness_ratio REAL,
    review_score REAL NOT NULL,
    review_time DATE,
    review_summary TEXT,
    review_text TEXT,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
)
'''
cursor.execute(create_ratings_table)

# Enable foreign key constraints
cursor.execute('PRAGMA foreign_keys = ON')

# Commit the schema changes
conn.commit()
print('tables created')



# Insert data using transactions & bulk insert
print('Inserting books data...')
books_new.to_sql('books', conn, if_exists='append', index=False, chunksize=500)
conn.commit()
print('Books inserted')

print('Inserting ratings data...')
ratings_new.to_sql('ratings', conn, if_exists='append', index=False, chunksize=500)
conn.commit()
print('Ratings inserted')

# create indexes after insert
cursor.execute('CREATE INDEX idx_ratings_book_id ON ratings (book_id)')
cursor.execute('CREATE INDEX idx_ratings_user_id ON ratings (user_id)')
conn.commit()
print('Indexes recreated')

# Close connection
conn.close()
print('Database setup complete')