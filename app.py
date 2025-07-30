from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('freelancer_platform.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists('freelancer_platform.db'):
        from init_db import init_database
        init_database()

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and 'freelancer_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def freelancer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'freelancer_id' not in session:
            flash('Freelancer access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('User access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
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
        user_type = request.form['user_type']
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            if user_type == 'user':
                conn.execute(
                    'INSERT INTO users (name, username, password, email) VALUES (?, ?, ?, ?)',
                    (name, username, hashed_password, email)
                )
                flash('Registration successful! You can now log in.', 'success')
            elif user_type == 'freelancer':
                conn.execute(
                    'INSERT INTO freelancers (name, username, password, email) VALUES (?, ?, ?, ?)',
                    (name, username, hashed_password, email)
                )
                flash('Registration successful! Please wait for admin approval before logging in.', 'success')
            
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists!', 'error')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        conn = get_db_connection()
        
        if user_type == 'user':
            user = conn.execute(
                'SELECT * FROM users WHERE username = ?', (username,)
            ).fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                session['name'] = user['name']
                
                if user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid username or password!', 'error')
                
        elif user_type == 'freelancer':
            freelancer = conn.execute(
                'SELECT * FROM freelancers WHERE username = ?', (username,)
            ).fetchone()
            
            if freelancer and check_password_hash(freelancer['password'], password):
                if not freelancer['approved']:
                    flash('Your account is pending admin approval!', 'error')
                else:
                    session['freelancer_id'] = freelancer['id']
                    session['username'] = freelancer['username']
                    session['name'] = freelancer['name']
                    return redirect(url_for('freelancer_dashboard'))
            else:
                flash('Invalid username or password!', 'error')
        
        conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/user_dashboard')
@user_required
def user_dashboard():
    conn = get_db_connection()
    projects = conn.execute(
        'SELECT * FROM projects WHERE user_id = ? ORDER BY id DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('user_dashboard.html', projects=projects)

@app.route('/freelancer_dashboard')
@freelancer_required
def freelancer_dashboard():
    conn = get_db_connection()
    projects = conn.execute(
        'SELECT p.*, u.name as client_name FROM projects p JOIN users u ON p.user_id = u.id WHERE p.status = "open" ORDER BY p.id DESC'
    ).fetchall()
    
    my_bids = conn.execute(
        'SELECT b.*, p.title as project_title FROM bids b JOIN projects p ON b.project_id = p.id WHERE b.freelancer_id = ? ORDER BY b.id DESC',
        (session['freelancer_id'],)
    ).fetchall()
    conn.close()
    return render_template('freelancer_dashboard.html', projects=projects, my_bids=my_bids)

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    
    pending_freelancers = conn.execute(
        'SELECT * FROM freelancers WHERE approved = 0'
    ).fetchall()
    
    all_users = conn.execute('SELECT * FROM users ORDER BY id DESC').fetchall()
    all_freelancers = conn.execute('SELECT * FROM freelancers ORDER BY id DESC').fetchall()
    all_projects = conn.execute(
        'SELECT p.*, u.name as client_name FROM projects p JOIN users u ON p.user_id = u.id ORDER BY p.id DESC'
    ).fetchall()
    all_bids = conn.execute(
        'SELECT b.*, p.title as project_title, f.name as freelancer_name FROM bids b JOIN projects p ON b.project_id = p.id JOIN freelancers f ON b.freelancer_id = f.id ORDER BY b.id DESC'
    ).fetchall()
    all_reviews = conn.execute(
        'SELECT r.*, p.title as project_title, u.name as client_name, f.name as freelancer_name FROM reviews r JOIN projects p ON r.project_id = p.id JOIN users u ON r.user_id = u.id JOIN freelancers f ON r.freelancer_id = f.id ORDER BY r.id DESC'
    ).fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         pending_freelancers=pending_freelancers,
                         all_users=all_users,
                         all_freelancers=all_freelancers,
                         all_projects=all_projects,
                         all_bids=all_bids,
                         all_reviews=all_reviews)

@app.route('/approve_freelancer/<int:freelancer_id>')
@admin_required
def approve_freelancer(freelancer_id):
    conn = get_db_connection()
    conn.execute('UPDATE freelancers SET approved = 1 WHERE id = ?', (freelancer_id,))
    conn.commit()
    conn.close()
    flash('Freelancer approved successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/add_project', methods=['GET', 'POST'])
@user_required
def add_project():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        budget = float(request.form['budget'])
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO projects (user_id, title, description, budget) VALUES (?, ?, ?, ?)',
            (session['user_id'], title, description, budget)
        )
        conn.commit()
        conn.close()
        
        flash('Project added successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    return render_template('add_project.html')

@app.route('/view_bids/<int:project_id>')
@user_required
def view_bids(project_id):
    conn = get_db_connection()
    
    project = conn.execute(
        'SELECT * FROM projects WHERE id = ? AND user_id = ?',
        (project_id, session['user_id'])
    ).fetchone()
    
    if not project:
        flash('Project not found!', 'error')
        return redirect(url_for('user_dashboard'))
    
    bids = conn.execute(
        'SELECT b.*, f.name as freelancer_name FROM bids b JOIN freelancers f ON b.freelancer_id = f.id WHERE b.project_id = ?',
        (project_id,)
    ).fetchall()
    
    conn.close()
    return render_template('view_bids.html', project=project, bids=bids)

@app.route('/select_bid/<int:bid_id>')
@user_required
def select_bid(bid_id):
    conn = get_db_connection()
    
    bid = conn.execute(
        'SELECT b.*, p.user_id FROM bids b JOIN projects p ON b.project_id = p.id WHERE b.id = ?',
        (bid_id,)
    ).fetchone()
    
    if not bid or bid['user_id'] != session['user_id']:
        flash('Bid not found!', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Update bid status and project status
    conn.execute('UPDATE bids SET status = "accepted" WHERE id = ?', (bid_id,))
    conn.execute('UPDATE bids SET status = "rejected" WHERE project_id = ? AND id != ?', 
                (bid['project_id'], bid_id))
    conn.execute('UPDATE projects SET status = "in_progress" WHERE id = ?', (bid['project_id'],))
    
    conn.commit()
    conn.close()
    
    flash('Bid selected successfully!', 'success')
    return redirect(url_for('view_bids', project_id=bid['project_id']))

@app.route('/place_bid/<int:project_id>', methods=['GET', 'POST'])
@freelancer_required
def place_bid(project_id):
    if request.method == 'POST':
        bid_amount = float(request.form['bid_amount'])
        timeline = request.form['timeline']
        
        conn = get_db_connection()
        
        # Check if freelancer already placed a bid
        existing_bid = conn.execute(
            'SELECT * FROM bids WHERE project_id = ? AND freelancer_id = ?',
            (project_id, session['freelancer_id'])
        ).fetchone()
        
        if existing_bid:
            flash('You have already placed a bid on this project!', 'error')
        else:
            conn.execute(
                'INSERT INTO bids (project_id, freelancer_id, bid_amount, timeline) VALUES (?, ?, ?, ?)',
                (project_id, session['freelancer_id'], bid_amount, timeline)
            )
            conn.commit()
            flash('Bid placed successfully!', 'success')
        
        conn.close()
        return redirect(url_for('freelancer_dashboard'))
    
    conn = get_db_connection()
    project = conn.execute(
        'SELECT p.*, u.name as client_name FROM projects p JOIN users u ON p.user_id = u.id WHERE p.id = ?',
        (project_id,)
    ).fetchone()
    conn.close()
    
    if not project:
        flash('Project not found!', 'error')
        return redirect(url_for('freelancer_dashboard'))
    
    return render_template('place_bid.html', project=project)

@app.route('/complete_project/<int:project_id>', methods=['GET', 'POST'])
@freelancer_required
def complete_project(project_id):
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('UPDATE projects SET status = "completed" WHERE id = ?', (project_id,))
        conn.commit()
        conn.close()
        flash('Project marked as completed!', 'success')
        return redirect(url_for('freelancer_dashboard'))
    
    conn = get_db_connection()
    project = conn.execute(
        'SELECT p.*, u.name as client_name FROM projects p JOIN users u ON p.user_id = u.id WHERE p.id = ?',
        (project_id,)
    ).fetchone()
    
    # Check if this freelancer has an accepted bid for this project
    bid = conn.execute(
        'SELECT * FROM bids WHERE project_id = ? AND freelancer_id = ? AND status = "accepted"',
        (project_id, session['freelancer_id'])
    ).fetchone()
    
    conn.close()
    
    if not bid:
        flash('You are not assigned to this project!', 'error')
        return redirect(url_for('freelancer_dashboard'))
    
    return render_template('complete_project.html', project=project)

@app.route('/add_review/<int:project_id>', methods=['GET', 'POST'])
@user_required
def add_review(project_id):
    if request.method == 'POST':
        rating = int(request.form['rating'])
        feedback = request.form['feedback']
        
        conn = get_db_connection()
        
        # Get the freelancer who worked on this project
        bid = conn.execute(
            'SELECT freelancer_id FROM bids WHERE project_id = ? AND status = "accepted"',
            (project_id,)
        ).fetchone()
        
        if bid:
            conn.execute(
                'INSERT INTO reviews (project_id, user_id, freelancer_id, rating, feedback) VALUES (?, ?, ?, ?, ?)',
                (project_id, session['user_id'], bid['freelancer_id'], rating, feedback)
            )
            conn.commit()
            flash('Review added successfully!', 'success')
        else:
            flash('No freelancer found for this project!', 'error')
        
        conn.close()
        return redirect(url_for('user_dashboard'))
    
    conn = get_db_connection()
    project = conn.execute(
        'SELECT * FROM projects WHERE id = ? AND user_id = ? AND status = "completed"',
        (project_id, session['user_id'])
    ).fetchone()
    
    if not project:
        flash('Project not found or not completed!', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Check if review already exists
    existing_review = conn.execute(
        'SELECT * FROM reviews WHERE project_id = ? AND user_id = ?',
        (project_id, session['user_id'])
    ).fetchone()
    
    conn.close()
    
    if existing_review:
        flash('You have already reviewed this project!', 'error')
        return redirect(url_for('user_dashboard'))
    
    return render_template('add_review.html', project=project)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)