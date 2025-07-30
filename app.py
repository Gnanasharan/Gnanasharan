from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database initialization
def init_db():
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            rating INTEGER NOT NULL,
            feedback TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (freelancer_id) REFERENCES freelancers (id)
        )
    ''')
    
    # Create admin user if not exists
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (name, username, password, role, email)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Admin User', 'admin', admin_password, 'admin', 'admin@example.com'))
    
    conn.commit()
    conn.close()

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('freelancer_platform.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        
        conn = get_db_connection()
        
        if role == 'user':
            # Check if username already exists
            cursor = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                flash('Username already exists!')
                return render_template('register.html')
            
            hashed_password = generate_password_hash(password)
            conn.execute('''
                INSERT INTO users (name, username, password, email)
                VALUES (?, ?, ?, ?)
            ''', (name, username, hashed_password, email))
            conn.commit()
            flash('Registration successful! You can now login.')
            return redirect(url_for('login'))
        
        elif role == 'freelancer':
            # Check if username already exists
            cursor = conn.execute('SELECT * FROM freelancers WHERE username = ?', (username,))
            if cursor.fetchone():
                flash('Username already exists!')
                return render_template('register.html')
            
            hashed_password = generate_password_hash(password)
            conn.execute('''
                INSERT INTO freelancers (name, username, password, email)
                VALUES (?, ?, ?, ?)
            ''', (name, username, hashed_password, email))
            conn.commit()
            flash('Registration successful! Please wait for admin approval.')
            return redirect(url_for('login'))
        
        conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        conn = get_db_connection()
        
        if role == 'user':
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = 'user'
                return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid username or password!')
        
        elif role == 'freelancer':
            freelancer = conn.execute('SELECT * FROM freelancers WHERE username = ?', (username,)).fetchone()
            if freelancer and check_password_hash(freelancer['password'], password):
                if freelancer['approved']:
                    session['user_id'] = freelancer['id']
                    session['username'] = freelancer['username']
                    session['role'] = 'freelancer'
                    return redirect(url_for('freelancer_dashboard'))
                else:
                    flash('Your account is pending approval by admin!')
            else:
                flash('Invalid username or password!')
        
        elif role == 'admin':
            user = conn.execute('SELECT * FROM users WHERE username = ? AND role = ?', (username, 'admin')).fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = 'admin'
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials!')
        
        conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user/dashboard')
def user_dashboard():
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    projects = conn.execute('''
        SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('user_dashboard.html', projects=projects)

@app.route('/user/add_project', methods=['GET', 'POST'])
def add_project():
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        budget = float(request.form['budget'])
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO projects (user_id, title, description, budget)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], title, description, budget))
        conn.commit()
        conn.close()
        
        flash('Project added successfully!')
        return redirect(url_for('user_dashboard'))
    
    return render_template('add_project.html')

@app.route('/user/project/<int:project_id>/bids')
def view_bids(project_id):
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    project = conn.execute('SELECT * FROM projects WHERE id = ? AND user_id = ?', (project_id, session['user_id'])).fetchone()
    if not project:
        flash('Project not found!')
        return redirect(url_for('user_dashboard'))
    
    bids = conn.execute('''
        SELECT b.*, f.name as freelancer_name, f.username as freelancer_username
        FROM bids b
        JOIN freelancers f ON b.freelancer_id = f.id
        WHERE b.project_id = ?
        ORDER BY b.bid_amount ASC
    ''', (project_id,)).fetchall()
    conn.close()
    
    return render_template('view_bids.html', project=project, bids=bids)

@app.route('/user/select_bid/<int:bid_id>')
def select_bid(bid_id):
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    bid = conn.execute('''
        SELECT b.*, p.user_id as project_user_id
        FROM bids b
        JOIN projects p ON b.project_id = p.id
        WHERE b.id = ?
    ''', (bid_id,)).fetchone()
    
    if not bid or bid['project_user_id'] != session['user_id']:
        flash('Bid not found!')
        return redirect(url_for('user_dashboard'))
    
    # Update bid status to accepted
    conn.execute('UPDATE bids SET status = ? WHERE id = ?', ('accepted', bid_id))
    # Update project status to in_progress
    conn.execute('UPDATE projects SET status = ? WHERE id = ?', ('in_progress', bid['project_id']))
    conn.commit()
    conn.close()
    
    flash('Bid selected successfully!')
    return redirect(url_for('user_dashboard'))

@app.route('/user/project/<int:project_id>/review', methods=['GET', 'POST'])
def add_review(project_id):
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    project = conn.execute('''
        SELECT p.*, b.freelancer_id
        FROM projects p
        JOIN bids b ON p.id = b.project_id
        WHERE p.id = ? AND p.user_id = ? AND b.status = 'accepted'
    ''', (project_id, session['user_id'])).fetchone()
    
    if not project:
        flash('Project not found or not completed!')
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        rating = int(request.form['rating'])
        feedback = request.form['feedback']
        
        # Check if review already exists
        existing_review = conn.execute('''
            SELECT * FROM reviews WHERE project_id = ? AND user_id = ?
        ''', (project_id, session['user_id'])).fetchone()
        
        if existing_review:
            flash('Review already submitted for this project!')
            return redirect(url_for('user_dashboard'))
        
        conn.execute('''
            INSERT INTO reviews (project_id, user_id, freelancer_id, rating, feedback)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_id, session['user_id'], project['freelancer_id'], rating, feedback))
        
        # Update project status to completed
        conn.execute('UPDATE projects SET status = ? WHERE id = ?', ('completed', project_id))
        conn.commit()
        conn.close()
        
        flash('Review submitted successfully!')
        return redirect(url_for('user_dashboard'))
    
    conn.close()
    return render_template('add_review.html', project=project)

@app.route('/freelancer/dashboard')
def freelancer_dashboard():
    if 'user_id' not in session or session['role'] != 'freelancer':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    available_projects = conn.execute('''
        SELECT * FROM projects WHERE status = 'open' ORDER BY created_at DESC
    ''').fetchall()
    
    my_bids = conn.execute('''
        SELECT b.*, p.title as project_title, p.budget as project_budget
        FROM bids b
        JOIN projects p ON b.project_id = p.id
        WHERE b.freelancer_id = ?
        ORDER BY b.created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    accepted_projects = conn.execute('''
        SELECT p.*, b.bid_amount, b.timeline
        FROM projects p
        JOIN bids b ON p.id = b.project_id
        WHERE b.freelancer_id = ? AND b.status = 'accepted'
        ORDER BY p.created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('freelancer_dashboard.html', 
                         available_projects=available_projects,
                         my_bids=my_bids,
                         accepted_projects=accepted_projects)

@app.route('/freelancer/project/<int:project_id>/bid', methods=['GET', 'POST'])
def place_bid(project_id):
    if 'user_id' not in session or session['role'] != 'freelancer':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    project = conn.execute('SELECT * FROM projects WHERE id = ? AND status = ?', (project_id, 'open')).fetchone()
    
    if not project:
        flash('Project not found or not available!')
        return redirect(url_for('freelancer_dashboard'))
    
    if request.method == 'POST':
        bid_amount = float(request.form['bid_amount'])
        timeline = request.form['timeline']
        
        # Check if already bid on this project
        existing_bid = conn.execute('''
            SELECT * FROM bids WHERE project_id = ? AND freelancer_id = ?
        ''', (project_id, session['user_id'])).fetchone()
        
        if existing_bid:
            flash('You have already bid on this project!')
            return redirect(url_for('freelancer_dashboard'))
        
        conn.execute('''
            INSERT INTO bids (project_id, freelancer_id, bid_amount, timeline)
            VALUES (?, ?, ?, ?)
        ''', (project_id, session['user_id'], bid_amount, timeline))
        conn.commit()
        conn.close()
        
        flash('Bid placed successfully!')
        return redirect(url_for('freelancer_dashboard'))
    
    conn.close()
    return render_template('place_bid.html', project=project)

@app.route('/freelancer/project/<int:project_id>/submit', methods=['GET', 'POST'])
def submit_project(project_id):
    if 'user_id' not in session or session['role'] != 'freelancer':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    project = conn.execute('''
        SELECT p.*, b.freelancer_id
        FROM projects p
        JOIN bids b ON p.id = b.project_id
        WHERE p.id = ? AND b.freelancer_id = ? AND b.status = 'accepted'
    ''', (project_id, session['user_id'])).fetchone()
    
    if not project:
        flash('Project not found or not assigned to you!')
        return redirect(url_for('freelancer_dashboard'))
    
    if request.method == 'POST':
        completion_details = request.form['completion_details']
        
        # Update project status to completed
        conn.execute('UPDATE projects SET status = ? WHERE id = ?', ('completed', project_id))
        conn.commit()
        conn.close()
        
        flash('Project submitted successfully!')
        return redirect(url_for('freelancer_dashboard'))
    
    conn.close()
    return render_template('submit_project.html', project=project)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get pending freelancers
    pending_freelancers = conn.execute('''
        SELECT * FROM freelancers WHERE approved = 0
    ''').fetchall()
    
    # Get all users
    users = conn.execute('SELECT * FROM users WHERE role != "admin"').fetchall()
    
    # Get all projects
    projects = conn.execute('''
        SELECT p.*, u.name as user_name
        FROM projects p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
    ''').fetchall()
    
    # Get all bids
    bids = conn.execute('''
        SELECT b.*, p.title as project_title, f.name as freelancer_name
        FROM bids b
        JOIN projects p ON b.project_id = p.id
        JOIN freelancers f ON b.freelancer_id = f.id
        ORDER BY b.created_at DESC
    ''').fetchall()
    
    # Get all reviews
    reviews = conn.execute('''
        SELECT r.*, p.title as project_title, u.name as user_name, f.name as freelancer_name
        FROM reviews r
        JOIN projects p ON r.project_id = p.id
        JOIN users u ON r.user_id = u.id
        JOIN freelancers f ON r.freelancer_id = f.id
        ORDER BY r.created_at DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html',
                         pending_freelancers=pending_freelancers,
                         users=users,
                         projects=projects,
                         bids=bids,
                         reviews=reviews)

@app.route('/admin/approve_freelancer/<int:freelancer_id>')
def approve_freelancer(freelancer_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('UPDATE freelancers SET approved = 1 WHERE id = ?', (freelancer_id,))
    conn.commit()
    conn.close()
    
    flash('Freelancer approved successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    flash('User deleted successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_freelancer/<int:freelancer_id>')
def delete_freelancer(freelancer_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM freelancers WHERE id = ?', (freelancer_id,))
    conn.commit()
    conn.close()
    
    flash('Freelancer deleted successfully!')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)