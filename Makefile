.PHONY: backend frontend backend-install frontend-install frontend-build install dev help

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

## Install backend dependencies, run migrations, and seed the database
backend-install:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	$(PYTHON) manage.py migrate
	$(PYTHON) manage.py seed_all

## Install frontend dependencies
frontend-install:
	cd frontend && npm install

## Install everything (backend + frontend)
install: backend-install frontend-install

## Build frontend and run the Django development server (serves both)
backend: frontend-build
	$(PYTHON) manage.py runserver

## Build frontend for production
frontend-build:
	@if [ -d frontend/node_modules ]; then cd frontend && npm run build; fi

## Run the frontend dev server
frontend:
	cd frontend && npm run dev

## Install dependencies and print instructions to start servers
dev: install
	@echo "Run 'make backend' and 'make frontend' in separate terminals"

## Show this help message
help:
	@echo "Usage: make [target]"
	@echo ""
	@awk -F':' '/^## / { desc = substr($$0, 4); getline; if (match($$0, /^[a-zA-Z_-]+:/)) { target = substr($$0, 1, RLENGTH-1); printf "  %-20s %s\n", target, desc } }' $(MAKEFILE_LIST)
