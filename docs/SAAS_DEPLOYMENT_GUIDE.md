# XunLong SaaS - Deployment Guide

Complete guide to deploying the XunLong SaaS application (Full-Stack AI Document Generation Platform).

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Production Deployment](#production-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Monitoring & Maintenance](#monitoring--maintenance)

## Architecture Overview

The XunLong SaaS application consists of:

- **Backend API**: FastAPI server handling authentication, projects, and document generation
- **Frontend**: React (Vite) single-page application with modern UI
- **Database**: SQLite (dev) or PostgreSQL (production)
- **Cache/Queue**: Redis for task queueing and caching
- **Core Engine**: XunLong deep search and document generation system

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────>│   Backend    │─────>│   XunLong   │
│   (React)   │      │   (FastAPI)  │      │   Engine    │
└─────────────┘      └──────────────┘      └─────────────┘
                           │                       │
                           ├──────> Redis          │
                           ├──────> Database       │
                           └──────> Storage ───────┘
```

## Prerequisites

### Required
- Python 3.10+
- Node.js 18+
- Redis (for task queue)
- Docker & Docker Compose (for containerized deployment)

### API Keys Required
- OpenAI API key (or alternative LLM provider)
- Bing Search API key (or SearXNG instance)
- Langfuse account (for monitoring)

## Local Development

### Backend Setup

1. **Navigate to project root**:
```bash
cd /path/to/xunlong
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

3. **Set up environment variables**:
```bash
# Copy and edit .env file with your API keys
cp .env.example .env
nano .env  # Add your API keys
```

4. **Run the backend**:
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/api/docs

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Run development server**:
```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

### Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or using system package manager
# macOS
brew install redis
brew services start redis

# Linux
sudo apt install redis-server
sudo systemctl start redis
```

## Docker Deployment

### Quick Start

1. **Build and start all services**:
```bash
docker-compose up -d
```

2. **Check service status**:
```bash
docker-compose ps
```

3. **View logs**:
```bash
docker-compose logs -f
```

4. **Stop services**:
```bash
docker-compose down
```

### Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Redis**: localhost:6379

### Persistent Data

Data is stored in Docker volumes:
- `redis-data`: Redis cache and queue data
- `./storage`: Generated documents and uploads (bind mount)

## Production Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose

# Clone repository
git clone https://github.com/yourusername/xunlong.git
cd xunlong
```

### 2. Configure Environment

```bash
# Create production .env file
cp .env.example .env
nano .env

# Set production values:
# - DEBUG=false
# - SECRET_KEY=strong-random-key
# - DATABASE_URL=postgresql://...  (if using PostgreSQL)
# - Add all required API keys
```

### 3. Use PostgreSQL (Recommended for Production)

Uncomment PostgreSQL service in `docker-compose.yml`:

```yaml
postgres:
  image: postgres:15-alpine
  container_name: xunlong-postgres
  environment:
    - POSTGRES_DB=xunlong
    - POSTGRES_USER=xunlong
    - POSTGRES_PASSWORD=your_secure_password
  volumes:
    - postgres-data:/var/lib/postgresql/data
```

Update `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://xunlong:your_secure_password@postgres:5432/xunlong
```

### 4. SSL/HTTPS Setup (Nginx Reverse Proxy)

Create `/etc/nginx/sites-available/xunlong`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Install SSL certificate (Let's Encrypt):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 5. Start Production Services

```bash
# Build and start
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Verify all services are running
docker-compose ps
```

### 6. Create First Admin User

```bash
# Access backend container
docker exec -it xunlong-backend bash

# Create admin user (Python script)
python -c "
from backend.database import SessionLocal, User
from backend.api.auth import get_password_hash

db = SessionLocal()
admin = User(
    email='admin@xunlong.ai',
    username='admin',
    hashed_password=get_password_hash('change-this-password'),
    full_name='Admin User',
    subscription_tier='enterprise',
    is_active=True,
    is_verified=True
)
db.add(admin)
db.commit()
print('Admin user created!')
"
```

## Environment Configuration

### Required Environment Variables

```bash
# === Core LLM Configuration ===
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...

# === Search ===
BING_API_KEY=...

# === Monitoring ===
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=https://us.cloud.langfuse.com

# === Backend ===
SECRET_KEY=your-super-secret-key-min-32-chars
DATABASE_URL=sqlite:///./xunlong_saas.db
REDIS_URL=redis://redis:6379/0

# === Optional: Email Notifications ===
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# === Optional: Stripe Payments ===
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Generating Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/health

# Frontend
curl http://localhost:3000

# Redis
redis-cli ping
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Backup Database

```bash
# SQLite
docker exec xunlong-backend cp /app/xunlong_saas.db /app/storage/backup-$(date +%Y%m%d).db

# PostgreSQL
docker exec xunlong-postgres pg_dump -U xunlong xunlong > backup-$(date +%Y%m%d).sql
```

### Update Application

```bash
# Pull latest code
git pull origin master

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Clean old images
docker image prune -a
```

### Monitor Resources

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

## Troubleshooting

### Backend not starting
- Check logs: `docker-compose logs backend`
- Verify environment variables in `.env`
- Ensure database is accessible
- Check Redis connection

### Frontend not loading
- Check nginx logs: `docker-compose logs frontend`
- Verify backend API is accessible
- Check browser console for errors

### WebSocket not connecting
- Verify WebSocket proxy configuration
- Check firewall rules
- Ensure Upgrade headers are set correctly

### Documents not generating
- Check XunLong engine logs
- Verify API keys are set correctly
- Check Langfuse connection
- Ensure sufficient storage space

## Performance Tuning

### Backend
- Use PostgreSQL for production
- Increase worker processes: `--workers 4`
- Configure connection pooling
- Enable Redis caching

### Frontend
- Enable gzip compression (already configured in nginx)
- Use CDN for static assets
- Implement lazy loading for routes

### Database
- Create indexes on frequently queried fields
- Regular VACUUM (PostgreSQL)
- Monitor slow queries

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Backup data regularly
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting

## Support

For issues or questions:
- GitHub Issues: https://github.com/yourusername/xunlong/issues
- Documentation: https://docs.xunlong.ai
- Email: support@xunlong.ai

---

**Last Updated**: November 2025
**Version**: 1.0.0

