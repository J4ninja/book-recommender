# import libraries
import pandas as pd
import numpy as np
import sqlite3

# read the book data
books = pd.read_csv('books_data.csv')

# read the ratings data
ratings = pd.read_csv('Books_rating.csv')

# join the book data with the ratings data on the 'Title' column
books_ratings = pd.merge(books, ratings, on='Title')

## authors ##
# remove middle brackets from the 'authors' column
books_ratings['authors'] = books_ratings['authors'].str.replace('[', '')
books_ratings['authors'] = books_ratings['authors'].str.replace(']', '')
# remove the single quotes from the 'authors' column
books_ratings['authors'] = books_ratings['authors'].str.replace("'", '')
# remove the leading and trailing double quotes from the 'authors' column
books_ratings['authors'] = books_ratings['authors'].str.strip('"')

## publish year ##
# extract the year from the 'published_date' column using the 'str.extract' method and regular expression pattern
books_ratings['published_year'] = books_ratings['publishedDate'].str.extract(r'(\d{4})')

## categories ##
# remove the middle brackets from the 'categories' column
books_ratings['categories'] = books_ratings['categories'].str.replace('[', '')
books_ratings['categories'] = books_ratings['categories'].str.replace(']', '')
# remove the leading and trailing single quotes from the 'categories' column
books_ratings['categories'] = books_ratings['categories'].str.strip("'")
# remove the single quotes from the 'categories' column
books_ratings['categories'] = books_ratings['categories'].str.replace("'", '')

## review time ##
# convert "review/time" from integer to datetime
books_ratings['review/time'] = pd.to_datetime(books_ratings['review/time'], unit='s')

## review id ##
# create a unique identifier for each row
books_ratings['review_id'] = books_ratings.index + 1

## review helpfulness ratio ##
# calculate the ratio of helpfulness for each review using the first number divided by the second number in the 'review/helpful' column split by the '/' character
books_ratings['helpfulness_ratio'] = books_ratings['review/helpfulness'].str.split('/').apply(lambda x: int(x[0]) / int(x[1]) if int(x[1]) != 0 else 0)

## NULL Title ##
# drop the rows with title NaN values
books_ratings = books_ratings.dropna(subset=['Title'])

## New book data ##
# decompose the data into two tables: books and reviews
books_new = books_ratings[['Id', 'Title', 'description', 'authors', 'image', 'previewLink', 'publisher',
       'publishedDate', 'published_year', 'infoLink', 'categories', 'ratingsCount']].drop_duplicates()

# replace column names with the new names
books_new.columns = ['book_id', 'title', 'description', 'authors', 'image', 'preview_link', 'publisher',
       'published_date', 'published_year', 'info_link', 'categories', 'ratings_count']

## New ratings data ##
# create a new table for the ratings data
ratings_new = books_ratings[['review_id', 'Id', 'Title', 'Price', 'User_id', 'profileName', 'helpfulness_ratio',
       'review/score', 'review/time', 'review/summary', 'review/text']].drop_duplicates()

# replace column names with the new names
ratings_new.columns = ['review_id', 'book_id', 'title', 'price', 'user_id', 'profile_name', 'helpfulness_ratio',
       'review_score', 'review_time', 'review_summary', 'review_text']

# save the books and ratings data to csv files
# books_new.to_csv('books_new.csv', index=False)
# ratings_new.to_csv('ratings_new.csv', index=False)


## Write the data to a SQLite database ##
# Create connection to SQLite
conn = sqlite3.connect("books.db")
cursor = conn.cursor()

# Drop tables if they exist
cursor.execute("DROP TABLE IF EXISTS ratings")
cursor.execute("DROP TABLE IF EXISTS books")

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
cursor.execute("PRAGMA foreign_keys = ON")

# Commit the schema changes
conn.commit()

# Insert data into books table
books_new.to_sql('books', conn, if_exists='append', index=False)
    
# Insert data into ratings table
ratings_new.to_sql('ratings', conn, if_exists='append', index=False)

# Commit all changes and close connection
conn.commit()
conn.close()