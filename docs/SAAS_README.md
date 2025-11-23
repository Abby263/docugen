# 🚀 XunLong SaaS - AI Document Generation Platform

A complete full-stack SaaS application that transforms your XunLong deep search engine into a beautiful web platform where users can generate professional documents, reports, and presentations via an intuitive UI.

![XunLong SaaS](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 🎯 User Features
- **Smart Document Generation**: AI-powered reports, analyses, research papers, and presentations
- **Multiple Document Types**: General reports, in-depth analysis, research papers, daily briefs, HTML presentations
- **Real-Time Progress**: WebSocket-powered live updates during document generation
- **Beautiful UI**: Modern, responsive React interface with Tailwind CSS
- **Project Management**: Create, track, and organize all your document projects
- **Advanced Analytics**: Comprehensive usage statistics and insights
- **Subscription Tiers**: Free, Pro, and Enterprise plans with different limits

### 🔧 Technical Features
- **RESTful API**: FastAPI backend with automatic OpenAPI documentation
- **Authentication**: JWT-based secure authentication system
- **Real-Time Updates**: WebSocket connections for live progress tracking
- **Async Processing**: Background task queue for document generation
- **Database**: SQLite (dev) / PostgreSQL (production) with SQLAlchemy ORM
- **Caching**: Redis for task queuing and caching
- **Monitoring**: Integrated Langfuse tracing for LLM operations
- **Docker Support**: Complete containerization with docker-compose
- **Production Ready**: HTTPS, health checks, logging, error handling

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│  - Dashboard  - Projects  - Analytics  - Settings       │
│  - WebSocket Client  - Real-time Updates                │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/WebSocket
┌────────────────▼────────────────────────────────────────┐
│                  Backend API (FastAPI)                   │
│  - Authentication  - Projects API  - Documents API       │
│  - WebSocket Manager  - Background Tasks                │
└───┬──────────────┬──────────────┬──────────────┬────────┘
    │              │              │              │
    ▼              ▼              ▼              ▼
┌────────┐    ┌─────────┐   ┌──────────┐   ┌─────────────┐
│Database│    │  Redis  │   │  Storage │   │   XunLong   │
│        │    │  Cache  │   │  System  │   │   Engine    │
│SQLite/ │    │  Queue  │   │  Files   │   │ Deep Search │
│Postgres│    │         │   │          │   │  Generator  │
└────────┘    └─────────┘   └──────────┘   └─────────────┘
```

## 📁 Project Structure

```
xunlong/
├── backend/                    # FastAPI Backend
│   ├── main.py                # Main FastAPI application
│   ├── config.py              # Configuration management
│   ├── database.py            # Database models and setup
│   ├── tasks.py               # Background task processing
│   ├── websocket_manager.py  # WebSocket connection handler
│   ├── api/                   # API endpoints
│   │   ├── auth.py           # Authentication
│   │   ├── projects.py       # Project management
│   │   ├── documents.py      # Document operations
│   │   └── analytics.py      # Usage analytics
│   └── Dockerfile            # Backend container
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── App.jsx           # Main app component
│   │   ├── pages/            # Page components
│   │   │   ├── LandingPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── ProjectsPage.jsx
│   │   │   ├── CreateProjectPage.jsx
│   │   │   ├── ProjectDetailPage.jsx
│   │   │   ├── AnalyticsPage.jsx
│   │   │   └── SettingsPage.jsx
│   │   ├── components/       # Reusable components
│   │   │   └── layouts/
│   │   │       └── DashboardLayout.jsx
│   │   ├── lib/              # Utilities
│   │   │   ├── api.js        # API client
│   │   │   └── websocket.js  # WebSocket hook
│   │   └── stores/           # State management
│   │       └── authStore.js  # Auth state
│   ├── Dockerfile            # Frontend container
│   ├── nginx.conf            # Nginx configuration
│   └── package.json
│
├── src/                       # Original XunLong Engine
│   ├── deep_search_agent.py
│   ├── agents/
│   ├── llm/
│   └── ...
│
├── docs/                      # Documentation
│   ├── SAAS_README.md        # This file
│   ├── SAAS_DEPLOYMENT_GUIDE.md
│   └── SAAS_USER_GUIDE.md
│
├── docker-compose.yml         # Container orchestration
├── Makefile                   # Convenient commands
└── .env                       # Environment variables
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (recommended)
- OpenAI API key (or alternative LLM provider)
- Bing Search API key

### Option 1: Docker (Recommended)

```bash
# 1. Clone and navigate
git clone https://github.com/yourusername/xunlong.git
cd xunlong

# 2. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 3. Start all services
make docker-up

# Or manually:
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Option 2: Local Development

**Backend:**
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Start backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
# Install dependencies
cd frontend
npm install

# Start dev server
npm run dev
```

## 📖 Documentation

- **[Deployment Guide](./SAAS_DEPLOYMENT_GUIDE.md)**: Complete deployment instructions
- **[User Guide](./SAAS_USER_GUIDE.md)**: End-user documentation
- **[API Documentation](http://localhost:8000/api/docs)**: Interactive API docs (when running)

## 🎨 Features Walkthrough

### 1. User Authentication
- Register with email, username, password
- JWT-based authentication
- Secure password hashing with bcrypt
- Token-based API access

### 2. Project Creation
Users can create projects by specifying:
- **Title**: Project name
- **Query**: Detailed research query
- **Document Type**: Report, Analysis, Research, Daily Brief, or PPT
- **Output Format**: HTML or Markdown

### 3. Real-Time Progress Tracking
- WebSocket connections provide live updates
- Progress bar shows generation status
- Notifications for completion/errors

### 4. Document Management
- View all projects with filtering
- Download generated documents
- Preview in browser
- Project statistics (processing time, search results, file size)

### 5. Analytics Dashboard
- Total projects and completion rate
- Monthly usage tracking
- Project distribution by type and status
- Activity trends and charts

### 6. Subscription Management
- **Free**: 5 documents/month
- **Pro**: 50 documents/month ($29)
- **Enterprise**: Unlimited (Custom pricing)

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following:

```bash
# LLM Configuration
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...

# Search
BING_API_KEY=...

# Monitoring
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=https://us.cloud.langfuse.com

# Backend
SECRET_KEY=your-super-secret-key-min-32-chars
DATABASE_URL=sqlite:///./xunlong_saas.db
REDIS_URL=redis://localhost:6379/0

# Optional: Email & Stripe
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
STRIPE_API_KEY=sk_test_...
```

See `.env.example` for complete configuration options.

## 🛠️ Available Commands

```bash
# Development
make install              # Install all dependencies
make dev-backend          # Start backend server
make dev-frontend         # Start frontend server
make dev-redis            # Start Redis

# Docker
make docker-up            # Start containers
make docker-down          # Stop containers
make docker-logs          # View logs
make docker-restart       # Restart containers

# Database
make db-reset             # Reset database
make backup-db            # Backup database

# Deployment
make deploy-build         # Build for production
make deploy-up            # Deploy to production

# Maintenance
make clean                # Clean build artifacts
make health-check         # Check service health
make logs-backend         # View backend logs
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run integration tests
make test-integration

# Manual testing
# 1. Create test user via API
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"testpass123"}'

# 2. Login and get token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"

# 3. Create project
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Project","query":"AI in healthcare","document_type":"report"}'
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Projects
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project details
- `PATCH /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project
- `POST /api/projects/{id}/cancel` - Cancel project

### Documents
- `GET /api/documents/{id}/download` - Download document
- `GET /api/documents/{id}/preview` - Preview document
- `GET /api/documents/{id}/metadata` - Get metadata

### Analytics
- `GET /api/analytics/dashboard` - Dashboard statistics
- `GET /api/analytics/usage` - Detailed usage stats

### WebSocket
- `WS /ws/{client_id}` - Real-time updates

## 🔒 Security

- HTTPS/SSL encryption
- JWT token authentication
- Password hashing with bcrypt
- SQL injection protection (SQLAlchemy ORM)
- CORS configuration
- Rate limiting (recommended for production)
- Environment variable secrets
- Input validation

## 🚀 Production Deployment

1. **Set up server** (Ubuntu 20.04+ recommended)
2. **Install Docker & Docker Compose**
3. **Clone repository**
4. **Configure environment** (production values)
5. **Use PostgreSQL** (uncomment in docker-compose.yml)
6. **Set up SSL** (Let's Encrypt + Nginx)
7. **Start services** (`make deploy-up`)
8. **Monitor** (health checks, logs)

See [Deployment Guide](./SAAS_DEPLOYMENT_GUIDE.md) for detailed instructions.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: [User Guide](./SAAS_USER_GUIDE.md) | [Deployment Guide](./SAAS_DEPLOYMENT_GUIDE.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/xunlong/issues)
- **Email**: support@xunlong.ai
- **Discord**: https://discord.gg/xunlong

## 🗺️ Roadmap

### Current Features (v1.0)
- ✅ User authentication and authorization
- ✅ Project creation and management
- ✅ Real-time progress tracking
- ✅ Multiple document types
- ✅ Analytics dashboard
- ✅ Subscription tiers (UI)
- ✅ Docker deployment

### Planned Features (v1.1+)
- [ ] Stripe payment integration
- [ ] API key generation for Pro/Enterprise
- [ ] Team collaboration features
- [ ] Custom templates
- [ ] Document sharing and public links
- [ ] Webhook notifications
- [ ] Multi-language support
- [ ] PDF export
- [ ] Advanced search filters
- [ ] Batch document generation
- [ ] Custom branding options

## 🙏 Acknowledgments

Built on top of the powerful **XunLong** deep search engine, combining:
- FastAPI for high-performance API
- React + Vite for modern frontend
- LangChain/LangGraph for AI orchestration
- Multiple LLM providers (OpenAI, Qwen, Deepseek, Zhipu)
- Langfuse for LLM observability

---

**Made with ❤️ by the XunLong Team**

**Last Updated**: November 2025 | **Version**: 1.0.0

