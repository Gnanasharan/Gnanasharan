from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, init_database
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize database on startup
init_database()

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for users, freelancers, and admin"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        conn = get_db_connection()
        
        if role == 'admin' or role == 'user':
            user = conn.execute(
                'SELECT * FROM users WHERE username = ? AND role = ?',
                (username, role)
            ).fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash('Login successful!', 'success')
                
                if role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid username or password!', 'error')
                
        elif role == 'freelancer':
            freelancer = conn.execute(
                'SELECT * FROM freelancers WHERE username = ?',
                (username,)
            ).fetchone()
            
            if freelancer and check_password_hash(freelancer['password'], password):
                if freelancer['approved']:
                    session['user_id'] = freelancer['id']
                    session['username'] = freelancer['username']
                    session['role'] = 'freelancer'
                    flash('Login successful!', 'success')
                    return redirect(url_for('freelancer_dashboard'))
                else:
                    flash('Your account is pending admin approval!', 'warning')
            else:
                flash('Invalid username or password!', 'error')
        
        conn.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration (clients)"""
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        
        # Check if username already exists
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if existing_user:
            flash('Username already exists!', 'error')
        else:
            hashed_password = generate_password_hash(password)
            conn.execute(
                'INSERT INTO users (name, username, password, role, email) VALUES (?, ?, ?, ?, ?)',
                (name, username, hashed_password, 'user', email)
            )
            conn.commit()
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('login'))
        
        conn.close()
    
    return render_template('register.html')

@app.route('/freelancer-register', methods=['GET', 'POST'])
def freelancer_register():
    """Freelancer registration (requires admin approval)"""
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        
        # Check if username already exists
        existing_freelancer = conn.execute(
            'SELECT id FROM freelancers WHERE username = ?', (username,)
        ).fetchone()
        
        if existing_freelancer:
            flash('Username already exists!', 'error')
        else:
            hashed_password = generate_password_hash(password)
            conn.execute(
                'INSERT INTO freelancers (name, username, password, email, approved) VALUES (?, ?, ?, ?, ?)',
                (name, username, hashed_password, email, False)
            )
            conn.commit()
            flash('Registration successful! Please wait for admin approval.', 'success')
            return redirect(url_for('login'))
        
        conn.close()
    
    return render_template('freelancer_register.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/user-dashboard')
def user_dashboard():
    """User (client) dashboard"""
    if 'user_id' not in session or session['role'] != 'user':
        flash('Please login as a user to access this page.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get user's projects
    projects = conn.execute(
        'SELECT * FROM projects WHERE user_id = ? ORDER BY id DESC',
        (session['user_id'],)
    ).fetchall()
    
    # Get bids for user's projects
    project_bids = {}
    for project in projects:
        bids = conn.execute(
            '''SELECT b.*, f.name as freelancer_name 
               FROM bids b 
               JOIN freelancers f ON b.freelancer_id = f.id 
               WHERE b.project_id = ?''',
            (project['id'],)
        ).fetchall()
        project_bids[project['id']] = bids
    
    conn.close()
    
    return render_template('user_dashboard.html', projects=projects, project_bids=project_bids)

@app.route('/freelancer-dashboard')
def freelancer_dashboard():
    """Freelancer dashboard"""
    if 'user_id' not in session or session['role'] != 'freelancer':
        flash('Please login as a freelancer to access this page.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get freelancer's bids
    bids = conn.execute(
        '''SELECT b.*, p.title as project_title, p.budget as project_budget,
                  u.name as client_name
           FROM bids b
           JOIN projects p ON b.project_id = p.id
           JOIN users u ON p.user_id = u.id
           WHERE b.freelancer_id = ?
           ORDER BY b.id DESC''',
        (session['user_id'],)
    ).fetchall()
    
    # Get available projects (not yet assigned)
    available_projects = conn.execute(
        '''SELECT p.*, u.name as client_name
           FROM projects p
           JOIN users u ON p.user_id = u.id
           WHERE p.status = "open"
           ORDER BY p.id DESC''',
    ).fetchall()
    
    conn.close()
    
    return render_template('freelancer_dashboard.html', bids=bids, available_projects=available_projects)

@app.route('/admin-dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Please login as admin to access this page.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get pending freelancer approvals
    pending_freelancers = conn.execute(
        'SELECT * FROM freelancers WHERE approved = 0'
    ).fetchall()
    
    # Get all users
    users = conn.execute('SELECT * FROM users WHERE role != "admin"').fetchall()
    
    # Get all projects
    projects = conn.execute(
        '''SELECT p.*, u.name as client_name
           FROM projects p
           JOIN users u ON p.user_id = u.id
           ORDER BY p.id DESC'''
    ).fetchall()
    
    # Get all bids
    bids = conn.execute(
        '''SELECT b.*, p.title as project_title, f.name as freelancer_name,
                  u.name as client_name
           FROM bids b
           JOIN projects p ON b.project_id = p.id
           JOIN freelancers f ON b.freelancer_id = f.id
           JOIN users u ON p.user_id = u.id
           ORDER BY b.id DESC'''
    ).fetchall()
    
    # Get all reviews
    reviews = conn.execute(
        '''SELECT r.*, p.title as project_title, f.name as freelancer_name,
                  u.name as client_name
           FROM reviews r
           JOIN projects p ON r.project_id = p.id
           JOIN freelancers f ON r.freelancer_id = f.id
           JOIN users u ON r.user_id = u.id
           ORDER BY r.id DESC'''
    ).fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         pending_freelancers=pending_freelancers,
                         users=users, projects=projects, bids=bids, reviews=reviews)

@app.route('/approve-freelancer/<int:freelancer_id>')
def approve_freelancer(freelancer_id):
    """Approve a freelancer"""
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute(
        'UPDATE freelancers SET approved = 1 WHERE id = ?',
        (freelancer_id,)
    )
    conn.commit()
    conn.close()
    
    flash('Freelancer approved successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/add-project', methods=['GET', 'POST'])
def add_project():
    """Add a new project"""
    if 'user_id' not in session or session['role'] != 'user':
        flash('Please login as a user to access this page.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        budget = float(request.form['budget'])
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO projects (user_id, title, description, budget, status) VALUES (?, ?, ?, ?, ?)',
            (session['user_id'], title, description, budget, 'open')
        )
        conn.commit()
        conn.close()
        
        flash('Project added successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    return render_template('add_project.html')

@app.route('/browse-projects')
def browse_projects():
    """Browse available projects (for freelancers)"""
    if 'user_id' not in session or session['role'] != 'freelancer':
        flash('Please login as a freelancer to access this page.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    projects = conn.execute(
        '''SELECT p.*, u.name as client_name
           FROM projects p
           JOIN users u ON p.user_id = u.id
           WHERE p.status = "open"
           ORDER BY p.id DESC'''
    ).fetchall()
    
    # Check which projects the freelancer has already bid on
    freelancer_bids = conn.execute(
        'SELECT project_id FROM bids WHERE freelancer_id = ?',
        (session['user_id'],)
    ).fetchall()
    
    bid_project_ids = [bid['project_id'] for bid in freelancer_bids]
    
    conn.close()
    
    return render_template('browse_projects.html', projects=projects, bid_project_ids=bid_project_ids)

@app.route('/place-bid/<int:project_id>', methods=['GET', 'POST'])
def place_bid(project_id):
    """Place a bid on a project"""
    if 'user_id' not in session or session['role'] != 'freelancer':
        flash('Please login as a freelancer to access this page.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get project details
    project = conn.execute(
        '''SELECT p.*, u.name as client_name
           FROM projects p
           JOIN users u ON p.user_id = u.id
           WHERE p.id = ?''',
        (project_id,)
    ).fetchone()
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('browse_projects'))
    
    # Check if freelancer already bid on this project
    existing_bid = conn.execute(
        'SELECT id FROM bids WHERE project_id = ? AND freelancer_id = ?',
        (project_id, session['user_id'])
    ).fetchone()
    
    if existing_bid:
        flash('You have already placed a bid on this project.', 'warning')
        return redirect(url_for('browse_projects'))
    
    if request.method == 'POST':
        bid_amount = float(request.form['bid_amount'])
        timeline = request.form['timeline']
        
        conn.execute(
            'INSERT INTO bids (project_id, freelancer_id, bid_amount, timeline, status) VALUES (?, ?, ?, ?, ?)',
            (project_id, session['user_id'], bid_amount, timeline, 'pending')
        )
        conn.commit()
        conn.close()
        
        flash('Bid placed successfully!', 'success')
        return redirect(url_for('browse_projects'))
    
    conn.close()
    
    return render_template('place_bid.html', project=project)

@app.route('/accept-bid/<int:bid_id>')
def accept_bid(bid_id):
    """Accept a bid for a project"""
    if 'user_id' not in session or session['role'] != 'user':
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get bid details
    bid = conn.execute(
        '''SELECT b.*, p.user_id
           FROM bids b
           JOIN projects p ON b.project_id = p.id
           WHERE b.id = ?''',
        (bid_id,)
    ).fetchone()
    
    if not bid or bid['user_id'] != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Accept the bid and close the project
    conn.execute('UPDATE bids SET status = "accepted" WHERE id = ?', (bid_id,))
    conn.execute('UPDATE projects SET status = "assigned" WHERE id = ?', (bid['project_id'],))
    
    # Reject other bids for the same project
    conn.execute(
        'UPDATE bids SET status = "rejected" WHERE project_id = ? AND id != ?',
        (bid['project_id'], bid_id)
    )
    
    conn.commit()
    conn.close()
    
    flash('Bid accepted successfully!', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/submit-project/<int:project_id>', methods=['GET', 'POST'])
def submit_project(project_id):
    """Freelancer submits completed project"""
    if 'user_id' not in session or session['role'] != 'freelancer':
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Check if freelancer has accepted bid for this project
    bid = conn.execute(
        '''SELECT b.* FROM bids b
           WHERE b.project_id = ? AND b.freelancer_id = ? AND b.status = "accepted"''',
        (project_id, session['user_id'])
    ).fetchone()
    
    if not bid:
        flash('You are not assigned to this project.', 'error')
        return redirect(url_for('freelancer_dashboard'))
    
    if request.method == 'POST':
        # Mark project as completed
        conn.execute(
            'UPDATE projects SET status = "completed" WHERE id = ?',
            (project_id,)
        )
        conn.commit()
        conn.close()
        
        flash('Project submitted successfully!', 'success')
        return redirect(url_for('freelancer_dashboard'))
    
    # Get project details
    project = conn.execute(
        '''SELECT p.*, u.name as client_name
           FROM projects p
           JOIN users u ON p.user_id = u.id
           WHERE p.id = ?''',
        (project_id,)
    ).fetchone()
    
    conn.close()
    
    return render_template('submit_project.html', project=project)

@app.route('/add-review/<int:project_id>', methods=['GET', 'POST'])
def add_review(project_id):
    """Add a review for completed project"""
    if 'user_id' not in session or session['role'] != 'user':
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get project and freelancer details
    project_data = conn.execute(
        '''SELECT p.*, b.freelancer_id, f.name as freelancer_name
           FROM projects p
           JOIN bids b ON p.id = b.project_id
           JOIN freelancers f ON b.freelancer_id = f.id
           WHERE p.id = ? AND p.user_id = ? AND b.status = "accepted" AND p.status = "completed"''',
        (project_id, session['user_id'])
    ).fetchone()
    
    if not project_data:
        flash('Project not found or not eligible for review.', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Check if review already exists
    existing_review = conn.execute(
        'SELECT id FROM reviews WHERE project_id = ? AND user_id = ?',
        (project_id, session['user_id'])
    ).fetchone()
    
    if existing_review:
        flash('You have already reviewed this project.', 'warning')
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        rating = int(request.form['rating'])
        feedback = request.form['feedback']
        
        conn.execute(
            'INSERT INTO reviews (project_id, user_id, freelancer_id, rating, feedback) VALUES (?, ?, ?, ?, ?)',
            (project_id, session['user_id'], project_data['freelancer_id'], rating, feedback)
        )
        conn.commit()
        conn.close()
        
        flash('Review added successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    conn.close()
    
    return render_template('add_review.html', project=project_data)

if __name__ == '__main__':
    app.run(debug=True)