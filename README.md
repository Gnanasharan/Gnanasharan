# Freelancer Hiring Platform

A complete web application built with Python Flask for connecting clients with freelancers. The platform allows clients to post projects, freelancers to bid on them, and includes an admin panel for platform management.

## Features

### User Roles

#### Admin
- Manages all platform information
- Views all users, freelancers, projects, bids, and reviews
- Approves freelancer registrations before they can log in
- Complete oversight of platform activities

#### Client (User)
- Registers and logs in without admin approval
- Posts projects with title, description, and budget
- Views and manages bids from freelancers
- Selects freelancers for projects
- Provides reviews and ratings after project completion

#### Freelancer
- Registers but requires admin approval before login
- Views available projects
- Places bids with cost and timeline estimates
- Marks projects as completed when finished
- Builds reputation through client reviews

### Core Functionality

- **Secure Authentication**: Hashed passwords using Werkzeug security
- **Project Management**: Complete project lifecycle from posting to completion
- **Bidding System**: Freelancers can bid on projects with custom pricing and timelines
- **Review System**: Clients can rate and review freelancers (1-5 stars)
- **Admin Dashboard**: Comprehensive management interface
- **Responsive Design**: Clean UI with white background and blue accent colors

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project files**

2. **Install dependencies**
   ```bash
   pip install Flask Werkzeug
   ```
   
   Or using the requirements file:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python init_db.py
   ```
   This creates the SQLite database with all required tables and a default admin user.

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your web browser and navigate to `http://localhost:5000`

## Default Login Credentials

### Admin Access
- **Username**: admin
- **Password**: admin123
- **Account Type**: Client/Admin

Use these credentials to access the admin dashboard and approve freelancer registrations.

## Project Structure

```
freelancer-platform/
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization script
├── requirements.txt      # Python dependencies
├── freelancer_platform.db # SQLite database (created after init)
├── static/
│   └── css/
│       └── style.css     # Application styling
└── templates/
    ├── base.html         # Base template with navigation
    ├── index.html        # Homepage
    ├── login.html        # Login page
    ├── register.html     # Registration page
    ├── user_dashboard.html      # Client dashboard
    ├── freelancer_dashboard.html # Freelancer dashboard
    ├── admin_dashboard.html     # Admin dashboard
    ├── add_project.html    # Project creation form
    ├── view_bids.html     # Bid viewing and selection
    ├── place_bid.html     # Bid submission form
    ├── complete_project.html # Project completion
    └── add_review.html    # Review submission form
```

## Database Schema

### Users Table
- id (Primary Key)
- name
- username (Unique)
- password (Hashed)
- role ('user' or 'admin')
- email

### Freelancers Table
- id (Primary Key)
- name
- username (Unique)
- password (Hashed)
- email
- approved (Boolean)

### Projects Table
- id (Primary Key)
- user_id (Foreign Key to Users)
- title
- description
- budget
- status ('open', 'in_progress', 'completed')

### Bids Table
- id (Primary Key)
- project_id (Foreign Key to Projects)
- freelancer_id (Foreign Key to Freelancers)
- bid_amount
- timeline
- status ('pending', 'accepted', 'rejected')

### Reviews Table
- id (Primary Key)
- project_id (Foreign Key to Projects)
- user_id (Foreign Key to Users)
- freelancer_id (Foreign Key to Freelancers)
- rating (1-5)
- feedback

## Usage Guide

### For Clients

1. **Registration**: Create an account as a "Client"
2. **Login**: Access your dashboard immediately after registration
3. **Post Projects**: Add projects with detailed descriptions and budgets
4. **Review Bids**: View and compare bids from interested freelancers
5. **Select Freelancer**: Choose the best bid for your project
6. **Project Completion**: Wait for freelancer to complete and submit work
7. **Add Review**: Rate and review the freelancer's work

### For Freelancers

1. **Registration**: Create an account as a "Freelancer"
2. **Wait for Approval**: Admin must approve your account before you can login
3. **Browse Projects**: View available projects that match your skills
4. **Place Bids**: Submit competitive bids with realistic timelines
5. **Work on Projects**: Complete assigned projects professionally
6. **Mark as Complete**: Submit completed work to the client
7. **Build Reputation**: Earn positive reviews to attract more clients

### For Administrators

1. **Login**: Use admin credentials to access the admin dashboard
2. **Approve Freelancers**: Review and approve pending freelancer registrations
3. **Monitor Platform**: View all users, projects, bids, and reviews
4. **Manage Activities**: Oversee platform operations and user activities

## Design Features

- **Clean Interface**: White background with blue accent colors
- **Responsive Design**: Works on desktop and mobile devices
- **Intuitive Navigation**: Clear menu structure for all user types
- **Professional Layout**: Card-based design with proper spacing
- **User-Friendly Forms**: Well-organized input fields with validation
- **Dashboard Analytics**: Statistics and overview for all user types

## Security Features

- Password hashing using Werkzeug security
- Session-based authentication
- Role-based access control
- Input validation and sanitization
- SQL injection prevention using parameterized queries

## Technologies Used

- **Backend**: Python Flask framework
- **Database**: SQLite with proper foreign key relationships
- **Frontend**: HTML5, CSS3, and Jinja2 templating
- **Security**: Werkzeug password hashing
- **Styling**: Custom CSS with modern design principles

## Development Notes

- The application uses Flask's development server (not for production)
- Database is created automatically when running `init_db.py`
- All templates extend a base template for consistent styling
- Flash messaging system for user feedback
- Decorator-based authentication for route protection

## Support

This is a complete, fully functional freelancer hiring platform that can be extended with additional features such as:

- Payment integration
- File upload capabilities
- Real-time messaging
- Advanced search and filtering
- Email notifications
- Portfolio management
- Advanced analytics

For any issues or questions, refer to the Flask documentation or contact the development team.
