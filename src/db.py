import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/clickstream.db")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
    """)

    # 2. Items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY,
            category TEXT NOT NULL
        )
    """)

    # 3. Events log table (Hot Path Ingestion)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            weight REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (item_id) REFERENCES items (item_id)
        )
    """)

    # 4. Pre-computed Recommendations table (Serving Lookup)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            predicted_score REAL NOT NULL,
            rank INTEGER NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, item_id)
        )
    """)

    conn.commit()
    conn.close()
    print("[INFO] Database schema initialized successfully.")

if __name__ == "__main__":
    init_db()
