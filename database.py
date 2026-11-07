import os
import sqlite3

# Define a persistent directory in macOS Application Support
APP_SUPPORT_DIR = os.path.join(
    os.path.expanduser("~"), "Library", "Application Support", "PitchPerfect"
)
os.makedirs(APP_SUPPORT_DIR, exist_ok=True)

DB_PATH = os.path.join(APP_SUPPORT_DIR, "pitchperfect.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Initializes database in persistent Application Support path."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """
    )

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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM users ORDER BY name")
    users = cursor.fetchall()
    conn.close()
    return users


def create_user(name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
        user_id = cursor.fetchone()[0]
    conn.close()
    return user_id


def save_score(user_id, accuracy, total_notes):
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
