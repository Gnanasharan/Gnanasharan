# Freelancer Hiring Platform

A complete web application built with Flask, SQLite, HTML, and CSS for connecting clients with freelancers.

## Features

### Admin Role
- Manage all platform information
- View all users, freelancers, projects, bids, and reviews
- Approve freelancer registrations before they can log in
- Delete users and freelancers

### Client (User) Role
- Register and login without admin approval
- Upload projects with name, description, and budget
- View bids from freelancers and select one
- Give reviews and ratings after project completion

### Freelancer Role
- Register (requires admin approval before login)
- View available projects
- Place bids with cost and timeline
- Submit completed project details to clients

## Database Schema

### Tables
- **Users**: id, name, username, password, role, email
- **Freelancers**: id, name, username, password, email, approved
- **Projects**: id, user_id, title, description, budget, status, created_at
- **Bids**: id, project_id, freelancer_id, bid_amount, timeline, status, created_at
- **Reviews**: id, project_id, user_id, freelancer_id, rating, feedback, created_at

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open your browser and go to `http://localhost:5000`

## Default Admin Account

- **Username**: admin
- **Password**: admin123

## Usage

### For Clients
1. Register as a "Client (User)"
2. Login and access your dashboard
3. Add new projects with title, description, and budget
4. View bids from freelancers and select the best one
5. Give reviews after project completion

### For Freelancers
1. Register as a "Freelancer"
2. Wait for admin approval
3. Login and browse available projects
4. Place bids with your proposed amount and timeline
5. Work on accepted projects and submit completion details

### For Admins
1. Login with admin credentials
2. Approve pending freelancer registrations
3. Monitor all platform activity
4. Manage users, projects, bids, and reviews

## Project Structure

```
freelancer-platform/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── user_dashboard.html
│   ├── add_project.html
│   ├── view_bids.html
│   ├── add_review.html
│   ├── freelancer_dashboard.html
│   ├── place_bid.html
│   ├── submit_project.html
│   └── admin_dashboard.html
└── static/
    └── css/
        └── style.css     # CSS styling
```

## Security Features

- Password hashing using Werkzeug
- Session management
- Role-based access control
- Input validation and sanitization

## UI/UX Features

- Clean, modern design with white background
- Blue clickable elements (buttons, links)
- Responsive design for mobile devices
- Status badges for different project states
- Flash messages for user feedback

## Database

The application uses SQLite as the database. The database file (`freelancer_platform.db`) will be created automatically when you first run the application.

## License

This project is open source and available under the MIT License.
