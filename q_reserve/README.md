# Q-Reserve - Professional Helpdesk System

Q-Reserve is a scalable, production-quality helpdesk system with AI enhancements, role-based workflows, and a modern minimalist UI built with Flask.

## 🚀 Features

### Core Features
- **Role-based authentication** (End User / Support Agent / Admin)
- **Comprehensive ticket management** with lifecycle tracking
- **Threaded conversations** and comment system
- **Advanced search and filtering** with full-text search
- **File attachments** with drag-and-drop support
- **Voting system** for ticket prioritization
- **Email notifications** with customizable templates
- **Responsive UI** with light/dark mode support

### AI-Powered Features
- **Smart duplicate detection** using embeddings
- **Auto-categorization** of tickets
- **Multi-language translation** support
- **Priority scoring** with sentiment analysis
- **SLA monitoring** and breach detection

### Advanced Features
- **Analytics dashboard** with performance metrics
- **Knowledge base** from resolved tickets
- **Gamification system** with badges and points
- **Real-time notifications** via WebSockets
- **External integrations** (Slack, Teams, WhatsApp)
- **Calendar integration** for deadlines
- **Custom workflows** and automation

## 🛠 Tech Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM with Flask-SQLAlchemy
- **PostgreSQL** - Primary database with pgvector for embeddings
- **Redis** - Caching and Celery broker
- **Celery** - Background job processing

### Frontend
- **Tailwind CSS** - Utility-first CSS framework
- **Alpine.js** - Lightweight JavaScript framework
- **Jinja2** - Template engine

### AI & Machine Learning
- **OpenAI API** - GPT models and embeddings
- **SentenceTransformers** - Local embedding models
- **pgvector** - Vector similarity search

### Infrastructure
- **Docker** - Containerization
- **GitHub Actions** - CI/CD pipeline
- **Flask-SocketIO** - Real-time communication
- **Flask-Mail** - Email notifications

## 📋 Requirements

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Node.js 16+ (for development tooling)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/q-reserve.git
cd q-reserve
```

### 2. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

### 3. Configure Environment Variables

Edit `.env` file with your configuration:

```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/q_reserve_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (optional - uses MailHog for development)
MAIL_SERVER=localhost
MAIL_PORT=1025

# AI Services (optional)
OPENAI_API_KEY=your-openai-api-key
```

### 4. Database Setup

```bash
# Initialize database
python scripts/init_db.py

# Run migrations (if any)
flask db upgrade

# Seed with sample data (optional)
python scripts/seed_data.py
```

### 5. Run the Application

```bash
# Start Redis (if not already running)
redis-server

# Start Celery worker (in separate terminal)
celery -A app.celery worker --loglevel=info

# Start Flask application
python app.py
```

Visit `http://localhost:5000` to access the application.

## 🐳 Docker Development

### Using Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Initialize database (first time only)
docker-compose exec web python scripts/init_db.py

# Seed with sample data
docker-compose exec web python scripts/seed_data.py
```

Services will be available at:
- Web application: http://localhost:5000
- MailHog (email testing): http://localhost:8025
- Redis: localhost:6379
- PostgreSQL: localhost:5432

## 📁 Project Structure

```
q_reserve/
├── apps/                    # Application modules
│   ├── auth/               # Authentication & authorization
│   ├── users/              # User management
│   ├── categories/         # Ticket categorization
│   ├── tickets/            # Core ticket functionality
│   ├── notifications/      # Notification system
│   ├── ai/                 # AI-powered features
│   └── dashboard/          # Analytics & dashboards
├── core/                   # Core application setup
│   ├── config.py          # Configuration management
│   ├── extensions.py      # Flask extensions
│   ├── factory.py         # Application factory
│   ├── errors.py          # Error handlers
│   └── utils.py           # Utility functions
├── templates/              # Jinja2 templates
│   ├── layouts/           # Base layouts
│   ├── components/        # Reusable components
│   ├── auth/              # Authentication pages
│   ├── tickets/           # Ticket management
│   └── emails/            # Email templates
├── static/                 # Static assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   ├── images/            # Images and icons
│   └── uploads/           # User uploads
├── scripts/               # Utility scripts
├── tests/                 # Test suite
├── migrations/            # Database migrations
└── docker/               # Docker configurations
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest tests/unit/test_user_model.py

# Run integration tests
pytest tests/integration/
```

## 🔒 Security Features

- **CSRF Protection** on all forms
- **Rate limiting** on authentication endpoints
- **Secure file uploads** with type validation
- **SQL injection protection** via SQLAlchemy ORM
- **XSS protection** via template auto-escaping
- **Secure session management**
- **Password strength requirements**
- **Role-based access control**

## 🌐 Deployment

### Environment Variables for Production

```bash
# Production settings
FLASK_ENV=production
DEBUG=false
SECRET_KEY=your-super-secret-production-key

# Database
DATABASE_URL=postgresql://user:pass@prod-db:5432/q_reserve_prod

# Email
MAIL_SERVER=smtp.your-provider.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-email-password

# Security
SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
```

### Deployment Options

#### Render
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically on push

#### Railway
```bash
railway login
railway init
railway add postgresql
railway add redis
railway deploy
```

#### DigitalOcean App Platform
1. Create new app from GitHub
2. Configure build and run commands
3. Add database and Redis components

#### Docker Production
```bash
# Build production image
docker build -t q-reserve:latest .

# Run with production compose
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Use meaningful commit messages
- Ensure all tests pass before submitting PR

## 📝 API Documentation

API documentation is available at `/api/docs` when running the application.

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL is running
pg_ctl status

# Verify connection string in .env
psql "postgresql://username:password@localhost:5432/q_reserve_dev"
```

**Redis Connection Error**
```bash
# Check Redis is running
redis-cli ping

# Should return PONG
```

**Email Not Sending**
```bash
# For development, use MailHog
docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog

# Check email configuration in .env
```

**AI Features Not Working**
- Ensure OpenAI API key is set in `.env`
- Check API quota and billing
- Verify pgvector extension is installed in PostgreSQL

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask community for the excellent framework
- Tailwind CSS for the utility-first approach
- OpenAI for providing powerful AI capabilities
- All contributors and testers

## 📞 Support

- 📧 Email: support@q-reserve.com
- 📖 Documentation: [docs.q-reserve.com](https://docs.q-reserve.com)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/q-reserve/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-org/q-reserve/discussions)

---

**Q-Reserve** - Revolutionizing customer support with AI-powered efficiency.