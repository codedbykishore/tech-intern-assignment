.PHONY: backend frontend backend-install frontend-install install dev

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

backend-install:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	$(PYTHON) manage.py migrate
	$(PYTHON) manage.py seed_all

frontend-install:
	cd frontend && npm install

install: backend-install frontend-install

backend:
	$(PYTHON) manage.py runserver

frontend:
	cd frontend && npm run dev

dev: install
	@echo "Run 'make backend' and 'make frontend' in separate terminals"
