# import libraries
import pandas as pd
import numpy as np
import sqlite3

# read the book data
books = pd.read_csv('data/books_data.csv')

# read the ratings data
ratings = pd.read_csv('data/Books_rating.csv')

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
# extract the year from the 'publishedDate' column using the 'str.extract' method and regular expression pattern
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
# calculate the ratio of helpfulness for each review using the first number divided by the second number in the 'review/helpfulness' column split by the '/' character
books_ratings['helpfulness_ratio'] = books_ratings['review/helpfulness'].str.split('/').apply(lambda x: int(x[0]) / int(x[1]) if int(x[1]) != 0 else 0)

## NULL Title ##
# drop the rows with Title NaN values
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

print(f'number of rows in dataframe {len(books_ratings)}')

# Drop duplicate reviews with same IDs 
ratings_new = books_ratings[['review_id', 'Id', 'Title', 'Price', 'User_id', 'profileName', 'helpfulness_ratio',
       'review/score', 'review/time', 'review/summary', 'review/text']].drop_duplicates(subset=['Id', 'review/text'])

# replace column names with the new names
ratings_new.columns = ['review_id', 'book_id', 'title', 'price', 'user_id', 'profile_name', 'helpfulness_ratio',
       'review_score', 'review_time', 'review_summary', 'review_text']

print(f'number of rows in dataframe after removing duplicates {len(ratings_new)}')

# save the books and ratings data to csv files
books_new.to_csv('data/books_new.csv', index=False)
ratings_new.to_csv('data/ratings_new.csv', index=False)
