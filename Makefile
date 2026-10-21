.PHONY: setup up down logs test lint fmt clean help

help:
	@echo "Available commands:"
	@echo "  make setup   - Create virtual environment and install dev dependencies"
	@echo "  make up      - Build and start all Docker services (API, Postgres, Qdrant, Redis)"
	@echo "  make down    - Stop all Docker services"
	@echo "  make logs    - Stream API service logs"
	@echo "  make test    - Run test suite"
	@echo "  make lint    - Run ruff linter and mypy type checks"
	@echo "  make fmt     - Auto-format code with ruff"
	@echo "  make clean   - Stop Docker services and delete named volumes (data resets!)"

setup:
	uv venv --python 3.11 && uv pip install -e ".[dev]" && pre-commit install

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f api

test:
	pytest

lint:
	ruff check .
	mypy backend/app

fmt:
	ruff format .
	ruff check --fix .

clean:
	docker compose down -v
