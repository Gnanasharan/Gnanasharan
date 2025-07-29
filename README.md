# FreelanceHub - Freelancer Hiring Platform

A complete web application built with Python Flask for connecting clients with freelancers. The platform enables clients to post projects, freelancers to place bids, and includes an admin system for managing the platform.

## Features

### For Clients (Users)
- ✅ Register and login without admin approval
- ✅ Post projects with title, description, and budget
- ✅ View bids from freelancers on their projects
- ✅ Accept bids and hire freelancers
- ✅ Add reviews and ratings after project completion

### For Freelancers
- ✅ Register (requires admin approval before login)
- ✅ Browse available projects
- ✅ Place bids with cost and timeline
- ✅ Submit completed projects to clients
- ✅ View bid status and project assignments

### For Administrators
- ✅ Approve freelancer registrations
- ✅ View and manage all users, projects, bids, and reviews
- ✅ Complete platform oversight and management

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with secure password hashing
- **Frontend**: HTML5, CSS3 (responsive design)
- **Security**: Werkzeug password hashing, session management

## Database Schema

### Tables:
- **users**: id, name, username, password, role, email
- **freelancers**: id, name, username, password, email, approved
- **projects**: id, user_id, title, description, budget, status
- **bids**: id, project_id, freelancer_id, bid_amount, timeline, status
- **reviews**: id, project_id, user_id, freelancer_id, rating, feedback

## Installation and Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd freelancer-platform
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your web browser and navigate to `http://localhost:5000`

## Default Login Credentials

### Admin Account
- **Username**: admin
- **Password**: admin123
- **Role**: Administrator

## Usage Guide

### Getting Started
1. **For Clients**: Register as a client → Login → Add projects → Review bids → Hire freelancers
2. **For Freelancers**: Register as freelancer → Wait for admin approval → Login → Browse projects → Place bids
3. **For Admins**: Login with admin credentials → Approve freelancers → Monitor platform activity

### Workflow
1. **Client posts a project** with requirements and budget
2. **Freelancers browse projects** and place competitive bids
3. **Client reviews bids** and selects the best freelancer
4. **Freelancer completes** the project and submits it
5. **Client reviews** the work and provides rating/feedback

## Project Structure

```
freelancer-platform/
├── app.py                 # Main Flask application
├── database.py           # Database setup and connection
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── templates/           # HTML templates
│   ├── base.html        # Base template with navigation
│   ├── index.html       # Home page
│   ├── login.html       # Login page
│   ├── register.html    # Client registration
│   ├── freelancer_register.html  # Freelancer registration
│   ├── user_dashboard.html       # Client dashboard
│   ├── freelancer_dashboard.html # Freelancer dashboard
│   ├── admin_dashboard.html      # Admin dashboard
│   ├── add_project.html         # Add new project
│   ├── browse_projects.html     # Browse available projects
│   ├── place_bid.html          # Place bid on project
│   ├── submit_project.html     # Submit completed project
│   └── add_review.html         # Add review and rating
├── static/
│   └── css/
│       └── style.css    # Stylesheet with blue theme
└── freelancer_platform.db  # SQLite database (created automatically)
```

## Features Implemented

✅ **Complete Authentication System**
- Secure registration and login
- Role-based access control
- Password hashing with Werkzeug

✅ **Project Management**
- Full CRUD operations for projects
- Status tracking (open, assigned, completed)
- Budget and description management

✅ **Bidding System**
- Freelancers can bid on projects
- Clients can accept/reject bids
- Timeline and cost proposals

✅ **Review System**
- 5-star rating system
- Written feedback
- Review visibility for platform users

✅ **Admin Dashboard**
- Freelancer approval workflow
- Platform statistics
- Complete user and project management

✅ **Responsive Design**
- Mobile-friendly interface
- Clean white background with blue accents
- Professional UI/UX design

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Role-based access protection
- SQL injection prevention with parameterized queries
- CSRF protection with form validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For questions or issues, please create an issue in the repository or contact the development team.

---

**FreelanceHub** - Connecting talented freelancers with great projects! 🚀
