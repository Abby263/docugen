# SaaS Platform - Makefile
# Convenient commands for development and deployment

.PHONY: help install dev-backend dev-frontend dev test clean docker-build docker-up docker-down deploy

help:  ## Show this help message
	@echo "SaaS Platform - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install:  ## Install all dependencies
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt
	pip install -r backend/requirements.txt
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ All dependencies installed!"

install-playwright:  ## Install Playwright browsers
	@echo "🎭 Installing Playwright browsers..."
	playwright install chromium
	@echo "✅ Playwright browsers installed!"

# Development
dev-backend:  ## Run backend development server
	@echo "🚀 Starting backend server..."
	cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:  ## Run frontend development server
	@echo "🚀 Starting frontend server..."
	cd frontend && npm run dev

dev-redis:  ## Start Redis in Docker
	@echo "🚀 Starting Redis..."
	docker run -d --name docugen-redis -p 6379:6379 redis:7-alpine

dev:  ## Start all development servers (requires multiple terminals)
	@echo "💡 Tip: Run these commands in separate terminals:"
	@echo "  1. make dev-redis"
	@echo "  2. make dev-backend"
	@echo "  3. make dev-frontend"

# Testing
test:  ## Run tests
	@echo "🧪 Running tests..."
	python -m pytest tests/

test-integration:  ## Run integration tests
	@echo "🧪 Running integration tests..."
	python -m pytest tests/integration/

# Docker
docker-build:  ## Build Docker images
	@echo "🐳 Building Docker images..."
	docker compose build

docker-up:  ## Start Docker containers
	@echo "🐳 Starting containers..."
	docker compose up -d
	@echo "✅ Containers started!"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/api/docs"

docker-down:  ## Stop Docker containers
	@echo "🐳 Stopping containers..."
	docker compose down

docker-logs:  ## View Docker logs
	docker compose logs -f

docker-restart:  ## Restart Docker containers
	@echo "🔄 Restarting containers..."
	docker compose restart

docker-clean:  ## Remove Docker containers and volumes
	@echo "🧹 Cleaning Docker resources..."
	docker compose down -v
	docker image prune -f

# Database
db-migrate:  ## Run database migrations
	@echo "📊 Running migrations..."
	cd backend && alembic upgrade head

db-reset:  ## Reset database (WARNING: Deletes all data)
	@echo "⚠️  Resetting database..."
	rm -f docugen_saas.db
	@echo "✅ Database reset!"

# Deployment
deploy-build:  ## Build for production
	@echo "🏗️  Building for production..."
	docker compose build --no-cache

deploy-up:  ## Deploy to production
	@echo "🚀 Deploying to production..."
	docker compose -f docker-compose.yml up -d
	@echo "✅ Deployed!"

deploy-down:  ## Stop production deployment
	docker compose down

# Maintenance
clean:  ## Clean build artifacts and cache
	@echo "🧹 Cleaning..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	cd frontend && rm -rf node_modules dist 2>/dev/null || true
	@echo "✅ Cleaned!"

logs-backend:  ## View backend logs
	docker compose logs -f backend

logs-frontend:  ## View frontend logs
	docker compose logs -f frontend

backup-db:  ## Backup database
	@echo "💾 Backing up database..."
	mkdir -p backups
	cp docugen_saas.db backups/docugen_saas_$(shell date +%Y%m%d_%H%M%S).db || \
	docker exec docugen-backend cp /app/docugen_saas.db /app/storage/backup-$(shell date +%Y%m%d_%H%M%S).db
	@echo "✅ Database backed up!"

# Quick commands
start: docker-up  ## Alias for docker-up

stop: docker-down  ## Alias for docker-down

restart: docker-restart  ## Alias for docker-restart

status:  ## Show container status
	docker compose ps

# Health checks
health-check:  ## Check if services are healthy
	@echo "🏥 Checking service health..."
	@echo "Backend API:"
	@curl -s http://localhost:8000/api/health | python -m json.tool || echo "❌ Backend not responding"
	@echo "\nFrontend:"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 && echo " ✅ Frontend OK" || echo "❌ Frontend not responding"
	@echo "\nRedis:"
	@docker exec docugen-redis redis-cli ping || echo "❌ Redis not responding"
