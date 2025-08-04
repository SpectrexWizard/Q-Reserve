# Helpdesk System MVP

A complete helpdesk/ticketing system built with Flask, featuring user authentication, role-based access control, ticket management, threaded comments, voting, and email notifications.

## Features

### Core Features
- **User Authentication**: JWT-based authentication with role management
- **Role-Based Access Control**: End users, agents, and administrators
- **Ticket Management**: Create, view, update, and manage support tickets
- **Threaded Comments**: Add comments and replies to tickets
- **Voting System**: Upvote/downvote tickets with unique constraints
- **File Attachments**: Upload files with validation and sanitization
- **Email Notifications**: Automated emails for ticket events
- **Search & Filtering**: Filter tickets by status, category, priority
- **Category Management**: Admin-controlled ticket categories

### Technical Features
- **JWT Authentication**: Secure token-based authentication
- **SQLite Database**: File-based database for easy deployment
- **Server-Side Rendering**: Jinja2 templates with Tailwind-like CSS
- **Responsive Design**: Mobile-friendly interface
- **Security**: Password hashing, file validation, RBAC

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone or extract the project**:
   ```bash
   cd helpdesk-mvp
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional):
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your settings (email configuration, etc.)
   # For development, the defaults will work
   ```

5. **Run the application**:
   ```bash
   python run.py
   ```

6. **Access the application**:
   - Open your browser to http://127.0.0.1:5000
   - The application will automatically create the database and default data

### Default Admin Account
- **Email**: admin@helpdesk.local
- **Password**: admin123

## Usage Guide

### User Roles

1. **End User**:
   - Create and view own tickets
   - Add comments to own tickets
   - Vote on tickets

2. **Agent**:
   - View and manage all tickets
   - Update ticket status and assignment
   - Add internal notes
   - All end user permissions

3. **Admin**:
   - Manage categories
   - All agent permissions
   - System administration

### Creating Your First Ticket

1. Register a new account or login
2. Click "New Ticket" 
3. Fill in the subject, category, and description
4. Optionally attach a file
5. Submit the ticket

### Managing Tickets (Agents/Admins)

1. View all tickets in the main dashboard
2. Filter by status, category, or search keywords
3. Click on a ticket to view details
4. Update status, priority, or assignment
5. Add comments or internal notes

### Email Notifications

The system sends email notifications for:
- New ticket creation (to ticket owner)
- Status changes (to ticket owner)
- New comments (to ticket owner)

**Note**: For development, emails are printed to the console. To enable real email sending, configure SMTP settings in `.env`.

## Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600

# Database
DATABASE_URL=sqlite:///helpdesk.db

# Email (optional - defaults to console output)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# File Uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=uploads/
ALLOWED_EXTENSIONS=txt,pdf,png,jpg,jpeg,gif,doc,docx
```

### Email Setup

To enable real email notifications:

1. Configure SMTP settings in `.env`
2. For Gmail, use an app password instead of your regular password
3. Restart the application

## API Endpoints

The application supports both web interface and JSON API:

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Tickets
- `GET /tickets/` - List tickets
- `POST /tickets/create` - Create ticket
- `GET /tickets/<id>` - View ticket
- `POST /tickets/<id>/update` - Update ticket

### Comments
- `POST /comments/create` - Add comment
- `POST /comments/<id>/update` - Update comment
- `POST /comments/<id>/delete` - Delete comment

### Voting
- `POST /votes/toggle` - Toggle vote
- `GET /votes/ticket/<id>` - Get vote info

### Categories (Admin only)
- `GET /categories/` - List categories
- `POST /categories/create` - Create category
- `POST /categories/<id>/update` - Update category

## Development

### Project Structure

```
helpdesk-mvp/
├── app/                    # Main application package
│   ├── __init__.py        # Application factory
│   ├── models.py          # Database models
│   ├── utils.py           # Utility functions and decorators
│   ├── auth/              # Authentication module
│   ├── tickets/           # Ticket management
│   ├── comments/          # Comments system
│   ├── votes/             # Voting system
│   ├── categories/        # Category management
│   ├── notifications/     # Email notifications
│   ├── templates/         # Jinja2 templates
│   └── static/           # CSS and JavaScript
├── config.py             # Configuration settings
├── run.py               # Development server
├── wsgi.py              # Production WSGI entry point
└── requirements.txt     # Python dependencies
```

### Adding New Features

1. **Models**: Add new database models in `app/models.py`
2. **Routes**: Create new blueprints in appropriate modules
3. **Templates**: Add HTML templates in `app/templates/`
4. **Styles**: Update `app/static/css/tailwind.css`

### Testing

The application includes test stubs in the `tests/` directory. To run tests:

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest
```

## Deployment

### Development
```bash
python run.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application
```

### Production Considerations

1. **Security**:
   - Change default secret keys
   - Use strong passwords
   - Enable HTTPS
   - Restrict file upload types

2. **Database**:
   - Consider PostgreSQL for production
   - Implement regular backups
   - Set up database migrations

3. **Performance**:
   - Use a reverse proxy (nginx)
   - Implement caching
   - Optimize database queries

4. **Monitoring**:
   - Set up logging
   - Monitor application metrics
   - Implement error tracking

## Troubleshooting

### Common Issues

1. **"Permission denied" errors**:
   - Ensure the `uploads/` directory is writable
   - Check file permissions

2. **Database errors**:
   - Delete `helpdesk.db` to reset the database
   - Check SQLite installation

3. **Email not sending**:
   - Verify SMTP configuration
   - Check console output for development mode

4. **Template not found**:
   - Ensure all template files are created
   - Check template paths in routes

### Getting Help

For issues or questions:
1. Check the browser console for JavaScript errors
2. Check the terminal/console for Python errors
3. Verify configuration in `.env`
4. Review the application logs

## License

This project is created as an MVP demonstration. Feel free to modify and extend it for your needs.

## Next Steps

Potential enhancements for production use:
- Database migrations with Flask-Migrate
- User profile management
- Dashboard with analytics
- SLA tracking
- Knowledge base integration
- Advanced search with Elasticsearch
- Real-time notifications with WebSockets
- Multi-tenant support
- API rate limiting
- Comprehensive test suite