# Q-Reserve Helpdesk System

A modern, scalable helpdesk system with AI enhancements, role-based workflows, and a beautiful minimalist UI.

## 🚀 Features

### Core Features
- **Role-based Authentication**: End User / Support Agent / Admin roles
- **Ticket Management**: Complete lifecycle from creation to resolution
- **Threaded Conversations**: Rich comment system with attachments
- **Voting System**: Upvote/downvote tickets with duplicate prevention
- **Search & Filtering**: Advanced search with multiple filters
- **Email Notifications**: Automated email notifications
- **File Attachments**: Drag-and-drop file uploads
- **Responsive Design**: Mobile-first design with dark/light mode

### AI Enhancements
- **Duplicate Detection**: AI-powered duplicate ticket suggestions
- **Auto-categorization**: Smart ticket categorization
- **Multi-language Translation**: Automatic content translation
- **Priority Scoring**: Sentiment analysis and urgency detection
- **Smart Suggestions**: AI-powered recommendations

### Advanced Features
- **Analytics Dashboard**: Resolution times, trends, SLA breaches
- **Knowledge Base**: Public knowledge base from resolved tickets
- **Gamification**: Badges and points system
- **External Integrations**: Slack/Teams/WhatsApp alerts
- **Calendar Integration**: Ticket deadline management
- **Real-time Notifications**: Live updates via WebSocket

## 🛠 Tech Stack

- **Backend**: Flask 3.0
- **Database**: PostgreSQL with pgvector extension
- **ORM**: SQLAlchemy / Flask-SQLAlchemy
- **Authentication**: Flask-Login with session-based auth
- **Background Jobs**: Celery with Redis broker
- **AI/ML**: OpenAI API, SentenceTransformers
- **Frontend**: Tailwind CSS, Alpine.js, Jinja2
- **Real-time**: Flask-SocketIO
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (for containerized setup)

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/q-reserve.git
   cd q-reserve
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Initialize the database**
   ```bash
   docker-compose exec web flask init-db
   docker-compose exec web flask seed-data
   docker-compose exec web flask create-admin
   ```

5. **Access the application**
   - Web: http://localhost:5000
   - Admin: http://localhost:5000/admin

### Option 2: Local Development

1. **Clone and setup**
   ```bash
   git clone https://github.com/your-username/q-reserve.git
   cd q-reserve
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database and API keys
   ```

3. **Setup database**
   ```bash
   # Create PostgreSQL database
   createdb q_reserve_db
   
   # Initialize database
   flask init-db
   flask seed-data
   flask create-admin
   ```

4. **Start services**
   ```bash
   # Terminal 1: Start Redis
   redis-server
   
   # Terminal 2: Start Celery
   celery -A core.extensions.celery worker --loglevel=info
   
   # Terminal 3: Start Celery Beat
   celery -A core.extensions.celery beat --loglevel=info
   
   # Terminal 4: Start Flask app
   flask run
   ```

## 🔧 Configuration

### Environment Variables

Key environment variables to configure:

```bash
# Flask Configuration
SECRET_KEY=your-super-secret-key
FLASK_ENV=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/q_reserve_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# AI Services
OPENAI_API_KEY=your-openai-api-key
DEEPL_API_KEY=your-deepl-api-key

# External Integrations
SLACK_WEBHOOK_URL=your-slack-webhook-url
TEAMS_WEBHOOK_URL=your-teams-webhook-url
```

### Feature Flags

Control feature availability:

```bash
ENABLE_AI_FEATURES=True
ENABLE_REAL_TIME_NOTIFICATIONS=True
ENABLE_FILE_UPLOADS=True
ENABLE_VOTING=True
ENABLE_TRANSLATION=True
```

## 📁 Project Structure

```
q_reserve/
├── apps/                    # Application modules
│   ├── auth/               # Authentication
│   ├── users/              # User management
│   ├── tickets/            # Ticket system
│   ├── categories/         # Category management
│   ├── notifications/      # Notification system
│   ├── ai/                # AI enhancements
│   └── dashboard/         # Analytics dashboard
├── core/                   # Core configuration
├── templates/              # Jinja2 templates
├── static/                 # Static files
├── tests/                  # Test suite
├── scripts/                # Utility scripts
├── docker/                 # Docker configurations
└── migrations/             # Database migrations
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov=core

# Run specific test file
pytest tests/unit/test_ticket_flow.py
```

## 🚀 Deployment

### Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn q_reserve:app`
5. Add environment variables from `.env.example`

### Railway

1. Connect your GitHub repository to Railway
2. Railway will auto-detect the Python app
3. Add environment variables in Railway dashboard
4. Deploy automatically on push

### DigitalOcean App Platform

1. Connect your GitHub repository
2. Select Python as the runtime
3. Set build command: `pip install -r requirements.txt`
4. Set run command: `gunicorn q_reserve:app`
5. Add environment variables

## 🔒 Security

- Session-based authentication with Flask-Login
- CSRF protection enabled
- Rate limiting with Flask-Limiter
- Input validation and sanitization
- SQL injection protection via SQLAlchemy
- XSS protection with content sanitization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki](https://github.com/your-username/q-reserve/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-username/q-reserve/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/q-reserve/discussions)

## 🗺 Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced analytics with ML insights
- [ ] Multi-tenant support
- [ ] API-first architecture
- [ ] Advanced workflow automation
- [ ] Integration marketplace
- [ ] White-label solution

## 🙏 Acknowledgments

- Flask community for the excellent framework
- Tailwind CSS for the beautiful UI components
- OpenAI for AI capabilities
- PostgreSQL team for the robust database
- All contributors and supporters

---

**Q-Reserve** - Modern helpdesk system for the future of customer support.