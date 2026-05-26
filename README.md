# Breathe ESG — Carbon Accounting Prototype

Django REST + React app that ingests emissions data from SAP, utility, and travel sources,
normalizes it to CO₂e, and provides a review dashboard for analysts.

## Prerequisites

- **Python 3.11+**
- **Node.js 20+** and **npm**
- **make** (see below)

### Installing make

| OS | Command |
|----|---------|
| **Ubuntu/Debian** | `sudo apt install build-essential` |
| **macOS** | `xcode-select --install` (includes make) |
| **Fedora/RHEL** | `sudo dnf install make` |
| **Arch** | `sudo pacman -S make` |
| **Windows** | Use [Chocolatey](https://chocolatey.org/): `choco install make` or WSL |

Verify: `make --version`

## Quick Start

```bash
# Install everything (venv, pip deps, migrate, seed, npm install)
make install

# Run backend (terminal 1)
make backend

# Run frontend (terminal 2)
make frontend
```

Open http://localhost:5173

### Individual targets

| Target | What it does |
|--------|--------------|
| `make backend-install` | venv → pip install → migrate → seed |
| `make frontend-install` | npm install |
| `make install` | both of the above |
| `make backend` | Django dev server on :8000 |
| `make frontend` | Vite dev server on :5173 |

### Manual setup (without make)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_all
python manage.py runserver &

cd frontend
npm install
npm run dev
```

## Credentials

| Role | Email | Password |
|------|-------|----------|
| Analyst | analyst@acme.com | password123 |
| Admin | admin@acme.com | password123 |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/login/ | JWT login (email + password) |
| POST | /api/auth/refresh/ | Refresh access token |
| POST | /api/ingestion/batches/upload/ | Upload CSV file |
| GET | /api/ingestion/batches/ | List import history |
| GET | /api/emissions/records/ | List emission records (filterable) |
| GET | /api/emissions/records/:id/ | Record detail with audit log |
| POST | /api/emissions/records/bulk_action/ | Approve/flag/reject/lock selected records |
| GET | /api/analytics/dashboard/?organization=1 | Dashboard aggregation |

## Project structure

```
├── config/               # Django settings, root URL conf
├── ingestion/            # Import batch tracking, raw row models, CSV parsers
│   ├── parsers/          # utility_parser, sap_parser, travel_parser
│   └── sample_data/      # utility_sample.csv, sap_sample.csv, travel_sample.csv
├── organizations/        # Multi-tenancy: Organization + OrganizationMember
├── emissions/            # EmissionRecord, AuditLog, EmissionFactor, seed command
├── analytics/            # Dashboard aggregation endpoint
├── frontend/             # Vite + React + TypeScript + Tailwind
│   └── src/
│       ├── components/   # dashboard/, upload/, review/
│       ├── pages/        # LoginPage, DashboardPage, UploadPage, ReviewPage
│       ├── hooks/        # useAuth (zustand store)
│       └── lib/          # Axios client with JWT interceptor
├── docs/                 # MODEL.md, DECISIONS.md, TRADEOFFS.md, SOURCES.md
├── Makefile
├── Dockerfile
└── render.yaml
```

## Deploy

See [render.yaml](render.yaml) for Render config. Required env vars:

- `DJANGO_SECRET_KEY` — generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DEBUG` — set to `False` in production

The Dockerfile builds the frontend into Django static files for single-container deployment.
