import os
import sqlite3
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_recommender.settings')
django.setup()

# Load environment variables
load_dotenv()

def get_env_variable(var_name):
    try:
        return os.getenv(var_name)
    except KeyError as exc:
        raise RuntimeError(f'Set the {var_name} environment variable.') from exc

# Aura connection details
USERNAME = get_env_variable('NEO4J_USERNAME')
PASSWORD = get_env_variable('NEO4J_PASSWORD')
URI = get_env_variable('NEO4J_URI')

driver = GraphDatabase.driver(f'neo4j+s://{URI}', auth=(USERNAME, PASSWORD))


# === Checkpoint utility ===

def load_checkpoint(label):
    if not os.path.exists('checkpoint.json'):
        return 0
    with open('checkpoint.json', 'r') as f:
        checkpoints = json.load(f)
    return checkpoints.get(label, 0)

def save_checkpoint(label, batch_index):
    checkpoints = {}
    if os.path.exists('checkpoint.json'):
        with open('checkpoint.json', 'r') as f:
            checkpoints = json.load(f)
    checkpoints[label] = batch_index
    with open('checkpoint.json', 'w') as f:
        json.dump(checkpoints, f)


# === Index/Constraint setup ===

def create_indexes_and_constraints():
    with driver.session() as session:
        session.run('CREATE INDEX book_id_index IF NOT EXISTS FOR (b:Book) ON (b.book_id)')
        session.run('CREATE INDEX user_id_index IF NOT EXISTS FOR (u:User) ON (u.user_id)')
        session.run('CREATE INDEX review_id_index IF NOT EXISTS FOR (r:Review) ON (r.review_id)')

#        session.run('CREATE CONSTRAINT unique_book_id IF NOT EXISTS FOR (b:Book) REQUIRE b.book_id IS UNIQUE')
#        session.run('CREATE CONSTRAINT unique_user_id IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE')
#        session.run('CREATE CONSTRAINT unique_review_id IF NOT EXISTS FOR (r:Review) REQUIRE r.review_id IS UNIQUE')

    print('Indexes and constraints created (if not already present)')


# === Cypher Insert Functions ===

def insert_books(tx, batch):
    tx.run('''
    UNWIND $batch AS row
    CREATE (b:Book {
        book_id: row.book_id,
        title: row.title,
        description: row.description,
        authors: row.authors,
        image: row.image,
        preview_link: row.preview_link,
        publisher: row.publisher,
        published_date: row.published_date,
        published_year: row.published_year,
        info_link: row.info_link,
        categories: row.categories,
        ratings_count: row.ratings_count
    })
    ''', batch=batch)

def insert_users(tx, batch):
    tx.run('''
    UNWIND $batch AS row
    CREATE (:User {
        user_id: row.user_id,
        profile_name: row.profile_name
    })
    ''', batch=batch)

def insert_reviews(tx, batch):
    tx.run('''
    UNWIND $batch AS row
    CREATE (r:Review {
        review_id: row.review_id,
        helpfulness_ratio: row.helpfulness_ratio,
        review_score: row.review_score,
        review_time: row.review_time,
        review_summary: row.review_summary,
        review_text: row.review_text,
        embedding: row.embedding
    })
    WITH r, row
    MATCH (b:Book {book_id: row.book_id})
    CREATE (r)-[:REVIEWS]->(b)
    WITH r, row
    MATCH (u:User {user_id: row.user_id})
    CREATE (u)-[:WROTE_REVIEW]->(r)
    CREATE (r)-[:WRITTEN_BY]->(u)
    ''', batch=batch)


# === Batch Runner ===

def process_in_batches(data, batch_size, insert_fn, label, model=None, embed_key=None):
    start_batch = load_checkpoint(label)
    total_batches = (len(data) + batch_size - 1) // batch_size

    with driver.session() as session:
        for i in range(start_batch * batch_size, len(data), batch_size):
            batch = data[i:i+batch_size]

            # Optional embedding step
            if model and embed_key:
                texts = [item.get(embed_key, '') or '' for item in batch]
                embeddings = model.encode(texts, batch_size=128, convert_to_numpy=True).tolist()
                for item, emb in zip(batch, embeddings):
                    item['embedding'] = emb

            session.execute_write(insert_fn, batch)
            print(f'[{label}] Inserted batch {i // batch_size + 1} of {total_batches} ({len(batch)} records)')
            save_checkpoint(label, i // batch_size + 1)


# === Load Data from SQLite ===

def main():
    skip_users_books = True
    create_indexes_and_constraints()

    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()

    if  not skip_users_books:
        # Books
        print('query book table')
        cursor.execute('SELECT * FROM books')
        books = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        process_in_batches(books, 1000, insert_books, label='books')

        # Users
        print('query reviews for users')
        cursor.execute('''
            SELECT user_id, MIN(profile_name) as profile_name
            FROM ratings
            WHERE user_id IS NOT NULL
            GROUP BY user_id
        ''')
        users = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        process_in_batches(users, 1000, insert_users, label='users')

    # Reviews
    print('query reviews table')
    cursor.execute('SELECT * FROM ratings')
    reviews = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    process_in_batches(
        reviews,
        batch_size=500,
        insert_fn=insert_reviews,
        label='reviews',
        model=model,
        embed_key='review_text'
    )

    driver.close()
    conn.close()

if __name__ == '__main__': 
    main()
