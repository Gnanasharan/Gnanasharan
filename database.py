import sqlite3
import hashlib
from werkzeug.security import generate_password_hash

DATABASE = 'freelancer_platform.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with all required tables"""
    conn = get_db_connection()
    
    # Create Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            email TEXT NOT NULL
        )
    ''')
    
    # Create Freelancers table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS freelancers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            approved BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # Create Projects table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            budget REAL NOT NULL,
            status TEXT DEFAULT 'open',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create Bids table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            freelancer_id INTEGER NOT NULL,
            bid_amount REAL NOT NULL,
            timeline TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (freelancer_id) REFERENCES freelancers (id)
        )
    ''')
    
    # Create Reviews table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            freelancer_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            feedback TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (freelancer_id) REFERENCES freelancers (id)
        )
    ''')
    
    # Create default admin user if not exists
    admin_exists = conn.execute(
        'SELECT id FROM users WHERE username = ?', ('admin',)
    ).fetchone()
    
    if not admin_exists:
        admin_password = generate_password_hash('admin123')
        conn.execute(
            'INSERT INTO users (name, username, password, role, email) VALUES (?, ?, ?, ?, ?)',
            ('Administrator', 'admin', admin_password, 'admin', 'admin@platform.com')
        )
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()