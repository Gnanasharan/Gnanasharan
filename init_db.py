import sqlite3

def init_database():
    conn = sqlite3.connect('freelancer_platform.db')
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS freelancers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            approved BOOLEAN DEFAULT 0
        )
    ''')
    
    # Create Projects table
    cursor.execute('''
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
    cursor.execute('''
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            freelancer_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            feedback TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (freelancer_id) REFERENCES freelancers (id)
        )
    ''')
    
    # Create default admin user (password: admin123)
    from werkzeug.security import generate_password_hash
    admin_password = generate_password_hash('admin123')
    cursor.execute('''
        INSERT OR IGNORE INTO users (name, username, password, role, email)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Admin User', 'admin', admin_password, 'admin', 'admin@platform.com'))
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()