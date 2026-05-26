# Breathe ESG — Carbon Accounting Prototype

Django REST + React app for ingesting, normalizing, and reviewing emissions data from SAP, utility, and travel sources.

## Quick Start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_all
python manage.py runserver &
cd frontend && npm install && npm run dev
```

Open http://localhost:5173

## Credentials

| Role | Email | Password |
|------|-------|----------|
| Analyst | analyst@acme.com | password123 |
| Admin | admin@acme.com | password123 |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/login/ | JWT login |
| POST | /api/auth/refresh/ | Refresh token |
| POST | /api/ingestion/batches/upload/ | Upload CSV |
| GET | /api/ingestion/batches/ | List imports |
| GET | /api/emissions/records/ | List emission records |
| GET | /api/emissions/records/:id/ | Record detail |
| POST | /api/emissions/records/bulk_action/ | Bulk approve/flag/reject/lock |
| GET | /api/analytics/dashboard/ | Dashboard stats |

## Deploy

See render.yaml for Render config. Set `DJANGO_SECRET_KEY` and `DEBUG=False`.
