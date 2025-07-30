# Freelancer Hiring Platform

A complete web application built with Python Flask, SQLite, HTML, and CSS for connecting clients with freelancers.

## Features

### For Clients (Users)
- ✅ Register and login without admin approval
- ✅ Post projects with title, description, and budget
- ✅ View all bids received for projects
- ✅ Select freelancers for projects
- ✅ Add reviews and ratings after project completion

### For Freelancers
- ✅ Register (requires admin approval before login)
- ✅ Browse available projects
- ✅ Place bids with cost and timeline
- ✅ Submit completed projects to clients

### For Administrators
- ✅ Approve freelancer registrations
- ✅ Manage all users, freelancers, projects, bids, and reviews
- ✅ Complete oversight of platform activity

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Session-based with password hashing

## Project Structure

```
freelancer-platform/
├── app.py                 # Main Flask application
├── database.py           # Database initialization and models
├── requirements.txt      # Python dependencies
├── freelancer_platform.db # SQLite database (created automatically)
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── user_dashboard.html
│   ├── freelancer_dashboard.html
│   ├── admin_dashboard.html
│   ├── add_project.html
│   ├── view_bids.html
│   ├── place_bid.html
│   ├── submit_project.html
│   └── add_review.html
└── static/
    └── css/
        └── style.css     # Main stylesheet
```

## Database Schema

### Users Table
- `id` (Primary Key)
- `name` (Text)
- `username` (Unique, Text)
- `password` (Hashed, Text)
- `role` (Text, default: 'user')
- `email` (Text)

### Freelancers Table
- `id` (Primary Key)
- `name` (Text)
- `username` (Unique, Text)
- `password` (Hashed, Text)
- `email` (Text)
- `approved` (Boolean, default: False)

### Projects Table
- `id` (Primary Key)
- `user_id` (Foreign Key to Users)
- `title` (Text)
- `description` (Text)
- `budget` (Real)
- `status` (Text, default: 'open')
- `created_at` (Timestamp)

### Bids Table
- `id` (Primary Key)
- `project_id` (Foreign Key to Projects)
- `freelancer_id` (Foreign Key to Freelancers)
- `bid_amount` (Real)
- `timeline` (Text)
- `status` (Text, default: 'pending')
- `created_at` (Timestamp)

### Reviews Table
- `id` (Primary Key)
- `project_id` (Foreign Key to Projects)
- `user_id` (Foreign Key to Users)
- `freelancer_id` (Foreign Key to Freelancers)
- `rating` (Integer, 1-5)
- `feedback` (Text)
- `created_at` (Timestamp)

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Python Flask
pip install flask

# Or using the requirements file
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python database.py
```

This will create the SQLite database with all required tables and a default admin user.

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Default Credentials

### Admin Account
- **Username**: admin
- **Password**: admin123
- **Role**: admin

Use these credentials to access the admin dashboard and approve freelancer registrations.

## Usage Guide

### Getting Started

1. **Visit the homepage** at `http://localhost:5000`
2. **Register an account**:
   - Choose "Client" to post projects
   - Choose "Freelancer" to bid on projects (requires admin approval)
3. **Login** with your credentials

### For Clients

1. **Post a Project**:
   - Login and go to your dashboard
   - Click "Post New Project"
   - Fill in title, description, and budget
   - Submit the project

2. **Manage Bids**:
   - View bids on your dashboard
   - Click "View Bids" for any project
   - Review freelancer profiles and bid details
   - Select the best bid

3. **Add Reviews**:
   - After project completion, add a review
   - Rate the freelancer (1-5 stars)
   - Provide feedback

### For Freelancers

1. **Wait for Approval**:
   - Register as a freelancer
   - Wait for admin approval
   - You'll receive a message if not yet approved

2. **Browse Projects**:
   - View available projects on your dashboard
   - Check project details and requirements

3. **Place Bids**:
   - Click "Place Bid" on any project
   - Enter your bid amount and timeline
   - Submit your proposal

4. **Submit Work**:
   - Once your bid is accepted
   - Complete the project work
   - Submit project as completed

### For Administrators

1. **Approve Freelancers**:
   - Login as admin
   - Go to "Pending Approvals" tab
   - Review and approve freelancer registrations

2. **Monitor Platform**:
   - View all users, projects, bids, and reviews
   - Monitor platform activity
   - Ensure quality control

## Features & Functionality

### Security Features
- ✅ Password hashing using SHA-256
- ✅ Session-based authentication
- ✅ Role-based access control
- ✅ Input validation and sanitization
- ✅ Protection against SQL injection

### User Experience
- ✅ Responsive design for mobile and desktop
- ✅ Clean white background with blue clickable elements
- ✅ Flash messages for user feedback
- ✅ Intuitive navigation and workflow
- ✅ Tabbed interface for complex pages

### Business Logic
- ✅ Project status management (open → in_progress → completed)
- ✅ Bid status management (pending → accepted/rejected)
- ✅ Freelancer approval workflow
- ✅ Review system with ratings

## Customization

### Styling
- Edit `static/css/style.css` to customize appearance
- All clickable elements use blue color scheme (#2563eb)
- Responsive design with mobile-first approach

### Database
- Modify `database.py` to add new tables or fields
- Update corresponding routes in `app.py`
- Create new templates as needed

### Features
- Add new routes in `app.py`
- Create corresponding HTML templates
- Update navigation in `base.html`

## Troubleshooting

### Common Issues

1. **"Template not found" errors**:
   - Ensure all template files are in the `templates/` directory
   - Check template names match route return statements

2. **CSS not loading**:
   - Verify `static/css/style.css` exists
   - Check browser cache (hard refresh)

3. **Database errors**:
   - Run `python database.py` to recreate database
   - Check file permissions

4. **Flask not starting**:
   - Install Flask: `pip install flask`
   - Check Python version compatibility

## License

This project is open source and available under the MIT License.

## Support

For questions or issues, please refer to the code comments or create an issue in the repository.
