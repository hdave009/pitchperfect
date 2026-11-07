import sqlite3
import os

DB_NAME = "pitchperfect.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Table 1: Users profile
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """
    )

    # Table 2: Game scores & performance tracking
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            accuracy REAL,
            total_notes INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """
    )

    conn.commit()
    conn.close()


def get_all_users():
    """Returns a list of all user tuples (id, name)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM users ORDER BY name")
    users = cursor.fetchall()
    conn.close()
    return users


def create_user(name):
    """Creates a new user and returns their assigned id."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        # User already exists, fetch their existing id
        cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
        user_id = cursor.fetchone()[0]
    conn.close()
    return user_id


def save_score(user_id, accuracy, total_notes):
    """Records a completed game score."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO scores (user_id, accuracy, total_notes)
        VALUES (?, ?, ?)
    """,
        (user_id, accuracy, total_notes),
    )
    conn.commit()
    conn.close()


def get_user_history(user_id):
    """Fetches past scores for trending history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT accuracy, timestamp FROM scores 
        WHERE user_id = ? 
        ORDER BY timestamp ASC LIMIT 10
    """,
        (user_id,),
    )
    history = cursor.fetchall()
    conn.close()
    return history
