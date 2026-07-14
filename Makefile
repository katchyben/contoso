BACKEND_DIR := backend
FRONTEND_DIR := frontend
E2E_DIR := e2e
DOCKER_DB_URL := postgresql+psycopg://postgres:postgres@localhost:5433/contoso

.DEFAULT_GOAL := help

.PHONY: help \
	install install-backend install-frontend install-e2e \
	dev-backend dev-frontend \
	up down restart logs seed \
	test test-backend test-e2e typecheck clean

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: install-backend install-frontend ## Install backend + frontend dependencies

install-backend: ## Install backend dependencies (uv)
	cd $(BACKEND_DIR) && uv sync

install-frontend: ## Install frontend dependencies (npm)
	cd $(FRONTEND_DIR) && npm install

install-e2e: ## Install e2e test dependencies + Chromium (one-time setup)
	cd $(E2E_DIR) && uv sync && uv run playwright install chromium

dev-backend: ## Run the backend dev server natively (port 8000, auto-reload)
	cd $(BACKEND_DIR) && uv run uvicorn app.main:app --reload

dev-frontend: ## Run the frontend dev server natively (Vite)
	cd $(FRONTEND_DIR) && npm run dev

up: ## Start the full stack via docker compose (db + backend + frontend)
	docker compose up -d

down: ## Stop the docker compose stack
	docker compose down

restart: ## Restart the docker compose stack
	docker compose restart

logs: ## Tail logs from the docker compose stack
	docker compose logs -f

seed: ## Seed the docker-compose Postgres database with fixture data
	cd $(BACKEND_DIR) && DATABASE_URL="$(DOCKER_DB_URL)" uv run python seed.py

test: test-backend ## Alias for test-backend

test-backend: ## Run the backend pytest suite (in-memory SQLite, no external services)
	cd $(BACKEND_DIR) && uv run pytest

test-e2e: ## Run the Playwright e2e suite (brings up the docker stack + seeds the db itself)
	cd $(E2E_DIR) && uv run pytest

typecheck: ## Type-check the frontend
	cd $(FRONTEND_DIR) && npx tsc --noEmit

clean: ## Remove Python bytecode and pytest caches
	find $(BACKEND_DIR) -type d -name "__pycache__" -not -path "*/.venv/*" -exec rm -rf {} +
	rm -rf $(BACKEND_DIR)/.pytest_cache $(E2E_DIR)/.pytest_cache
