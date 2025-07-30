from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
from datetime import datetime
from database import init_database, hash_password

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('freelancer_platform.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    """Decorator to require login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        
        if not all([name, username, password, email, role]):
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        hashed_password = hash_password(password)
        conn = get_db_connection()
        
        try:
            if role == 'user':
                # Regular user registration (no approval needed)
                conn.execute('''
                    INSERT INTO users (name, username, password, role, email)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, username, hashed_password, role, email))
                flash('Registration successful! You can now log in.', 'success')
            elif role == 'freelancer':
                # Freelancer registration (requires approval)
                conn.execute('''
                    INSERT INTO freelancers (name, username, password, email, approved)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, username, hashed_password, email, False))
                flash('Registration submitted! Please wait for admin approval.', 'info')
            
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'error')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        if not all([username, password, role]):
            flash('All fields are required.', 'error')
            return render_template('login.html')
        
        hashed_password = hash_password(password)
        conn = get_db_connection()
        
        if role in ['user', 'admin']:
            user = conn.execute('''
                SELECT * FROM users WHERE username = ? AND password = ? AND role = ?
            ''', (username, hashed_password, role)).fetchone()
            
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['name'] = user['name']
                session['role'] = user['role']
                flash(f'Welcome back, {user["name"]}!', 'success')
                
                if role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid credentials.', 'error')
        
        elif role == 'freelancer':
            freelancer = conn.execute('''
                SELECT * FROM freelancers WHERE username = ? AND password = ? AND approved = 1
            ''', (username, hashed_password)).fetchone()
            
            if freelancer:
                session['user_id'] = freelancer['id']
                session['username'] = freelancer['username']
                session['name'] = freelancer['name']
                session['role'] = 'freelancer'
                flash(f'Welcome back, {freelancer["name"]}!', 'success')
                return redirect(url_for('freelancer_dashboard'))
            else:
                # Check if freelancer exists but not approved
                unapproved = conn.execute('''
                    SELECT * FROM freelancers WHERE username = ? AND password = ?
                ''', (username, hashed_password)).fetchone()
                
                if unapproved:
                    flash('Your account is pending admin approval.', 'info')
                else:
                    flash('Invalid credentials.', 'error')
        
        conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    """User dashboard"""
    if session['role'] != 'user':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    projects = conn.execute('''
        SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('user_dashboard.html', projects=projects)

@app.route('/freelancer_dashboard')
@login_required
def freelancer_dashboard():
    """Freelancer dashboard"""
    if session['role'] != 'freelancer':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    # Get available projects
    projects = conn.execute('''
        SELECT p.*, u.name as client_name FROM projects p
        JOIN users u ON p.user_id = u.id
        WHERE p.status = 'open'
        ORDER BY p.created_at DESC
    ''').fetchall()
    
    # Get my bids
    my_bids = conn.execute('''
        SELECT b.*, p.title as project_title, u.name as client_name
        FROM bids b
        JOIN projects p ON b.project_id = p.id
        JOIN users u ON p.user_id = u.id
        WHERE b.freelancer_id = ?
        ORDER BY b.created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    return render_template('freelancer_dashboard.html', projects=projects, my_bids=my_bids)

@app.route('/admin_dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    conn = get_db_connection()
    
    # Get pending freelancer approvals
    pending_freelancers = conn.execute('''
        SELECT * FROM freelancers WHERE approved = 0
    ''').fetchall()
    
    # Get all users
    users = conn.execute('SELECT * FROM users').fetchall()
    
    # Get all freelancers
    freelancers = conn.execute('SELECT * FROM freelancers').fetchall()
    
    # Get all projects
    projects = conn.execute('''
        SELECT p.*, u.name as client_name FROM projects p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
    ''').fetchall()
    
    # Get all bids
    bids = conn.execute('''
        SELECT b.*, p.title as project_title, f.name as freelancer_name, u.name as client_name
        FROM bids b
        JOIN projects p ON b.project_id = p.id
        JOIN freelancers f ON b.freelancer_id = f.id
        JOIN users u ON p.user_id = u.id
        ORDER BY b.created_at DESC
    ''').fetchall()
    
    # Get all reviews
    reviews = conn.execute('''
        SELECT r.*, p.title as project_title, u.name as client_name, f.name as freelancer_name
        FROM reviews r
        JOIN projects p ON r.project_id = p.id
        JOIN users u ON r.user_id = u.id
        JOIN freelancers f ON r.freelancer_id = f.id
        ORDER BY r.created_at DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         pending_freelancers=pending_freelancers,
                         users=users, freelancers=freelancers,
                         projects=projects, bids=bids, reviews=reviews)

@app.route('/approve_freelancer/<int:freelancer_id>')
@login_required
@admin_required
def approve_freelancer(freelancer_id):
    """Approve freelancer registration"""
    conn = get_db_connection()
    conn.execute('UPDATE freelancers SET approved = 1 WHERE id = ?', (freelancer_id,))
    conn.commit()
    conn.close()
    flash('Freelancer approved successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/add_project', methods=['GET', 'POST'])
@login_required
def add_project():
    """Add new project"""
    if session['role'] != 'user':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        budget = request.form['budget']
        
        if not all([title, description, budget]):
            flash('All fields are required.', 'error')
            return render_template('add_project.html')
        
        try:
            budget = float(budget)
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO projects (user_id, title, description, budget)
                VALUES (?, ?, ?, ?)
            ''', (session['user_id'], title, description, budget))
            conn.commit()
            conn.close()
            flash('Project added successfully!', 'success')
            return redirect(url_for('user_dashboard'))
        except ValueError:
            flash('Invalid budget amount.', 'error')
    
    return render_template('add_project.html')

@app.route('/view_bids/<int:project_id>')
@login_required
def view_bids(project_id):
    """View bids for a project"""
    if session['role'] != 'user':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Check if project belongs to current user
    project = conn.execute('''
        SELECT * FROM projects WHERE id = ? AND user_id = ?
    ''', (project_id, session['user_id'])).fetchone()
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Get bids for this project
    bids = conn.execute('''
        SELECT b.*, f.name as freelancer_name, f.email as freelancer_email
        FROM bids b
        JOIN freelancers f ON b.freelancer_id = f.id
        WHERE b.project_id = ?
        ORDER BY b.created_at DESC
    ''', (project_id,)).fetchall()
    
    conn.close()
    return render_template('view_bids.html', project=project, bids=bids)

@app.route('/select_bid/<int:bid_id>')
@login_required
def select_bid(bid_id):
    """Select a bid for a project"""
    if session['role'] != 'user':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get bid and project info
    bid = conn.execute('''
        SELECT b.*, p.user_id FROM bids b
        JOIN projects p ON b.project_id = p.id
        WHERE b.id = ?
    ''', (bid_id,)).fetchone()
    
    if bid and bid['user_id'] == session['user_id']:
        # Update bid status to accepted
        conn.execute('UPDATE bids SET status = ? WHERE id = ?', ('accepted', bid_id))
        # Update project status to in_progress
        conn.execute('UPDATE projects SET status = ? WHERE id = ?', ('in_progress', bid['project_id']))
        # Reject other bids for this project
        conn.execute('''
            UPDATE bids SET status = ? WHERE project_id = ? AND id != ?
        ''', ('rejected', bid['project_id'], bid_id))
        conn.commit()
        flash('Bid selected successfully!', 'success')
    else:
        flash('Bid not found.', 'error')
    
    conn.close()
    return redirect(url_for('user_dashboard'))

@app.route('/place_bid/<int:project_id>', methods=['GET', 'POST'])
@login_required
def place_bid(project_id):
    """Place a bid on a project"""
    if session['role'] != 'freelancer':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get project details
    project = conn.execute('''
        SELECT p.*, u.name as client_name FROM projects p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ? AND p.status = 'open'
    ''', (project_id,)).fetchone()
    
    if not project:
        flash('Project not found or not available.', 'error')
        return redirect(url_for('freelancer_dashboard'))
    
    # Check if already bid
    existing_bid = conn.execute('''
        SELECT * FROM bids WHERE project_id = ? AND freelancer_id = ?
    ''', (project_id, session['user_id'])).fetchone()
    
    if existing_bid:
        flash('You have already placed a bid on this project.', 'error')
        return redirect(url_for('freelancer_dashboard'))
    
    if request.method == 'POST':
        bid_amount = request.form['bid_amount']
        timeline = request.form['timeline']
        
        if not all([bid_amount, timeline]):
            flash('All fields are required.', 'error')
            return render_template('place_bid.html', project=project)
        
        try:
            bid_amount = float(bid_amount)
            conn.execute('''
                INSERT INTO bids (project_id, freelancer_id, bid_amount, timeline)
                VALUES (?, ?, ?, ?)
            ''', (project_id, session['user_id'], bid_amount, timeline))
            conn.commit()
            flash('Bid placed successfully!', 'success')
            return redirect(url_for('freelancer_dashboard'))
        except ValueError:
            flash('Invalid bid amount.', 'error')
    
    conn.close()
    return render_template('place_bid.html', project=project)

@app.route('/submit_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def submit_project(project_id):
    """Submit completed project"""
    if session['role'] != 'freelancer':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Check if freelancer has accepted bid for this project
    bid = conn.execute('''
        SELECT b.*, p.title as project_title FROM bids b
        JOIN projects p ON b.project_id = p.id
        WHERE b.project_id = ? AND b.freelancer_id = ? AND b.status = 'accepted'
    ''', (project_id, session['user_id'])).fetchone()
    
    if not bid:
        flash('Project not found or not assigned to you.', 'error')
        return redirect(url_for('freelancer_dashboard'))
    
    if request.method == 'POST':
        # Update project status to completed
        conn.execute('UPDATE projects SET status = ? WHERE id = ?', ('completed', project_id))
        conn.commit()
        flash('Project submitted successfully!', 'success')
        return redirect(url_for('freelancer_dashboard'))
    
    conn.close()
    return render_template('submit_project.html', bid=bid)

@app.route('/add_review/<int:project_id>', methods=['GET', 'POST'])
@login_required
def add_review(project_id):
    """Add review for completed project"""
    if session['role'] != 'user':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get project and freelancer info
    project_info = conn.execute('''
        SELECT p.*, f.name as freelancer_name, b.freelancer_id
        FROM projects p
        JOIN bids b ON p.id = b.project_id AND b.status = 'accepted'
        JOIN freelancers f ON b.freelancer_id = f.id
        WHERE p.id = ? AND p.user_id = ? AND p.status = 'completed'
    ''', (project_id, session['user_id'])).fetchone()
    
    if not project_info:
        flash('Project not found or not completed.', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Check if review already exists
    existing_review = conn.execute('''
        SELECT * FROM reviews WHERE project_id = ? AND user_id = ?
    ''', (project_id, session['user_id'])).fetchone()
    
    if existing_review:
        flash('You have already reviewed this project.', 'error')
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        rating = request.form['rating']
        feedback = request.form['feedback']
        
        if not rating:
            flash('Rating is required.', 'error')
            return render_template('add_review.html', project=project_info)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                flash('Rating must be between 1 and 5.', 'error')
                return render_template('add_review.html', project=project_info)
            
            conn.execute('''
                INSERT INTO reviews (project_id, user_id, freelancer_id, rating, feedback)
                VALUES (?, ?, ?, ?, ?)
            ''', (project_id, session['user_id'], project_info['freelancer_id'], rating, feedback))
            conn.commit()
            flash('Review added successfully!', 'success')
            return redirect(url_for('user_dashboard'))
        except ValueError:
            flash('Invalid rating.', 'error')
    
    conn.close()
    return render_template('add_review.html', project=project_info)

if __name__ == '__main__':
    init_database()
    app.run(debug=True)