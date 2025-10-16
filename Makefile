.PHONY: help setup install clean test run worker beat all stop

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help:
	@echo "$(BLUE)Social Media Pipeline POC - Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup Commands:$(NC)"
	@echo "  make setup          - Complete POC setup (install deps, init DB)"
	@echo "  make install        - Install Python dependencies only"
	@echo "  make init-db        - Initialize SQLite database"
	@echo ""
	@echo "$(GREEN)Run Commands:$(NC)"
	@echo "  make run            - Start FastAPI server"
	@echo "  make worker         - Start Celery worker"
	@echo "  make beat           - Start Celery beat scheduler"
	@echo "  make all            - Start all services (parallel)"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make test           - Run all tests"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo "  make lint           - Run code linting"
	@echo "  make format         - Format code with black"
	@echo ""
	@echo "$(GREEN)Data & Management:$(NC)"
	@echo "  make ingest         - Manually trigger tweet ingestion"
	@echo "  make shell          - Open Python shell with app context"
	@echo "  make redis-cli      - Open Redis CLI"
	@echo ""
	@echo "$(GREEN)Cleanup:$(NC)"
	@echo "  make clean          - Remove generated files"
	@echo "  make clean-all      - Remove everything (including venv)"
	@echo "  make stop           - Stop all running services"

setup: install init-db
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo "$(YELLOW)Next: Edit .env and add your Twitter API token$(NC)"

install:
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install -r requirements.txt
	python -m textblob.download_corpora
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

init-db:
	@echo "$(BLUE)Initializing database...$(NC)"
	@python3 -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"
	@echo "$(GREEN)✓ Database initialized$(NC)"

run:
	@echo "$(BLUE)Starting FastAPI server...$(NC)"
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	@echo "$(BLUE)Starting Celery worker...$(NC)"
	celery -A app.celery_app worker --loglevel=info

beat:
	@echo "$(BLUE)Starting Celery beat...$(NC)"
	celery -A app.celery_app beat --loglevel=info

all:
	@echo "$(BLUE)Starting all services...$(NC)"
	@echo "$(YELLOW)Use Ctrl+C to stop all services$(NC)"
	@trap 'kill 0' EXIT; \
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 & \
	celery -A app.celery_app worker --loglevel=info & \
	celery -A app.celery_app beat --loglevel=info & \
	wait

stop:
	@echo "$(BLUE)Stopping services...$(NC)"
	@pkill -f "celery -A app.celery_app" || true
	@pkill -f "uvicorn app.main:app" || true
	@echo "$(GREEN)✓ Services stopped$(NC)"

test:
	@echo "$(BLUE)Running tests...$(NC)"
	pytest tests/ -v

test-coverage:
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest tests/ --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)Coverage report: htmlcov/index.html$(NC)"

test-integration:
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest tests/ -v --run-integration

lint:
	@echo "$(BLUE)Running linters...$(NC)"
	flake8 app/ --max-line-length=120 --ignore=E203,W503
	mypy app/ --ignore-missing-imports

format:
	@echo "$(BLUE)Formatting code...$(NC)"
	black app/ tests/
	isort app/ tests/

ingest:
	@echo "$(BLUE)Triggering manual tweet ingestion...$(NC)"
	@python3 -c "from app.tasks.data_ingestion import fetch_and_store_tweets; print(fetch_and_store_tweets())"

shell:
	@echo "$(BLUE)Opening Python shell...$(NC)"
	@python3 -c "import asyncio; from app.database import AsyncSessionLocal; from app.models import *; from app.services.ai_service import AIService; from app.services.data_service import DataService; import IPython; IPython.embed()"

redis-cli:
	@echo "$(BLUE)Opening Redis CLI...$(NC)"
	redis-cli

check-redis:
	@echo "$(BLUE)Checking Redis connection...$(NC)"
	@redis-cli ping && echo "$(GREEN)✓ Redis is running$(NC)" || echo "$(RED)✗ Redis is not running$(NC)"

check-env:
	@echo "$(BLUE)Checking environment configuration...$(NC)"
	@test -f .env && echo "$(GREEN)✓ .env file exists$(NC)" || echo "$(RED)✗ .env file missing$(NC)"
	@grep -q "TWITTER_BEARER_TOKEN=your_bearer_token_here" .env && echo "$(YELLOW)⚠ Twitter token not configured$(NC)" || echo "$(GREEN)✓ Twitter token configured$(NC)"

health:
	@echo "$(BLUE)Checking application health...$(NC)"
	@curl -s http://localhost:8000/health | python3 -m json.tool

logs:
	@echo "$(BLUE)Showing application logs...$(NC)"
	tail -f logs/app.log

celery-status:
	@echo "$(BLUE)Checking Celery status...$(NC)"
	celery -A app.celery_app inspect active
	celery -A app.celery_app inspect stats

clean:
	@echo "$(BLUE)Cleaning generated files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage
	@echo "$(GREEN)✓ Cleaned$(NC)"

clean-all: clean stop
	@echo "$(BLUE)Removing everything...$(NC)"
	rm -rf venv/
	rm -f social_media.db
	rm -rf logs/
	@echo "$(GREEN)✓ Complete cleanup done$(NC)"

dev-deps:
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	pip install black flake8 mypy isort ipython pytest-cov

backup-db:
	@echo "$(BLUE)Backing up database...$(NC)"
	@mkdir -p backups
	cp social_media.db backups/social_media_$(shell date +%Y%m%d_%H%M%S).db
	@echo "$(GREEN)✓ Database backed up$(NC)"

restore-db:
	@echo "$(BLUE)Available backups:$(NC)"
	@ls -lh backups/
	@echo "$(YELLOW)To restore: cp backups/[filename] social_media.db$(NC)"

.env:
	@echo "$(BLUE)Creating .env file...$(NC)"
	cp .env.example .env
	@echo "$(GREEN)✓ .env created$(NC)"
	@echo "$(YELLOW)Remember to edit .env and add your credentials!$(NC)"

