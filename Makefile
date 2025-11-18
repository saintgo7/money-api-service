.PHONY: help install dev build up down logs test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install Python dependencies
	pip install -r requirements.txt

dev: ## Run development server
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

build: ## Build Docker images
	docker-compose build

up: ## Start all services with Docker Compose
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs
	docker-compose logs -f api

test: ## Run tests
	pytest tests/ -v

clean: ## Clean up containers and volumes
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

migrate: ## Run database migrations
	alembic upgrade head

dashboard-dev: ## Run dashboard in development mode
	cd dashboard && npm run dev

dashboard-build: ## Build dashboard for production
	cd dashboard && npm run build

format: ## Format code with black
	black src/ tests/

lint: ## Lint code with pylint
	pylint src/
