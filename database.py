import sqlite3
from werkzeug.security import generate_password_hash

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect('db/financial_app.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database with the required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # User table with roles
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Analyst', 'CEO', 'GroupOwner'))
    )
    ''')

    # Company table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        group_name TEXT
    )
    ''')

    # Financial data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS financial_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        year INTEGER NOT NULL,
        data_json TEXT NOT NULL,
        source_document TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (id),
        UNIQUE(company_id, year)
    )
    ''')

    # Permissions table to link users to companies
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_company_permissions (
        user_id INTEGER NOT NULL,
        company_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (company_id) REFERENCES companies (id),
        PRIMARY KEY (user_id, company_id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def add_user(username, password, role):
    """Adds a new user to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )
        conn.commit()
        print(f"User '{username}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists.")
    finally:
        conn.close()

if __name__ == '__main__':
    # This block will run only when database.py is executed directly.
    # It's useful for setting up the initial database structure.
    init_db()