# WhatsApp-to-Invoice AI Workflow System

An AI workflow product demo for SMEs that turns customer messages into structured business actions: extraction, pricing, invoices or quotations, follow-up tasks, daily reports, and automation-ready outputs.

## Product Summary

This system is designed for teams that receive customer requests over WhatsApp-like channels and want a lightweight operational workflow instead of manual message handling.

Core flow:

Customer message  
-> AI extraction  
-> product or service matching  
-> pricing  
-> draft invoice or quotation  
-> operational task generation  
-> dashboard visibility  
-> daily report and automation dispatch

## What It Does

- Understands inbound customer requests with a replaceable AI provider layer
- Extracts intent, items or services, dates, locations, and missing information
- Matches extracted requests against a catalog of products or services
- Calculates subtotal, delivery fee, tax placeholder, and total
- Creates draft orders and invoices or quotations
- Generates internal follow-up tasks automatically
- Exposes a product-style operator UI at `/ui`
- Provides daily report generation and automation logging
- Supports n8n-triggered automation for daily reporting

## Business Scenarios Included

- Pharmacy order workflow
- Cleaning quotation workflow
- Maintenance service request workflow

These scenarios are implemented as domain-specific behavior on top of one shared workflow core.

## Architecture

Backend:

- `FastAPI` for API endpoints and frontend hosting
- `SQLAlchemy` for data persistence
- `SQLite` for local/demo storage
- `Jinja2` for invoice HTML rendering
- `pydantic-settings` for environment-driven configuration

Frontend:

- Product-style HTML/CSS/JavaScript operator console served by FastAPI at `/ui`
- Optional Streamlit dashboard kept in the repo as an internal demo surface

Automation:

- SMTP email dispatch for daily reports
- n8n integration via protected automation endpoints

Testing:

- `pytest`

## Main Interfaces

Operator UI:

- `GET /ui`

API:

- `GET /health`
- `POST /messages/extract`
- `POST /orders/from-message`
- `POST /reports/generate`
- `POST /reports/send`
- `POST /automation/daily-report`

Interactive docs:

- `GET /docs`

## Project Structure

```text
app/
  api/routes/
  ai/providers/
  core/
  models/
  repositories/
  schemas/
  services/
  templates/
dashboard/
data/
frontend/
n8n/
tests/
```

## Local Run

### 1. Create environment

```powershell
conda create -n env-workflow python=3.11 -y
conda activate env-workflow
pip install -r requirements.txt
```

### 2. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Update `.env` with real values for:

- `API_KEY`
- `N8N_WEBHOOK_SECRET`
- SMTP settings if email sending is required

### 3. Start the API

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Open the operator UI

```text
http://127.0.0.1:8000/ui
```

### 5. Optional Streamlit dashboard

```powershell
python -m streamlit run dashboard\streamlit_app.py
```

## Docker Run

Build:

```powershell
docker build -t whatsapp-to-invoice-ai .
```

Run:

```powershell
docker run --rm -p 8000:8000 --env-file .env whatsapp-to-invoice-ai
```

Notes:

- The included Docker image is optimized for API + product UI serving.
- SQLite inside the container is ephemeral unless you bind-mount storage.
- For persistent demo data, mount a host directory and point `DATABASE_URL` to that path.

Example with mounted SQLite file:

```powershell
docker run --rm -p 8000:8000 --env-file .env -v ${PWD}\runtime:/runtime whatsapp-to-invoice-ai
```

Then set:

```env
DATABASE_URL=sqlite:////runtime/sme_ai_workflow.db
```

## n8n Integration

This project treats n8n as the orchestration layer, not the place where business logic lives.

Recommended pattern:

1. n8n `Schedule Trigger`
2. n8n `HTTP Request`
3. Call `POST /automation/daily-report`
4. Use header `x-webhook-secret`

Reference files:

- [n8n/README.md](n8n/README.md)
- [n8n/workflow_examples/daily-report-trigger.json](n8n/workflow_examples/daily-report-trigger.json)

## Test Suite

Run all automated tests:

```powershell
python -m pytest -q
```

Current verified coverage includes:

- health endpoint
- data models
- AI message extraction
- catalog matching
- pricing
- order and invoice workflow
- task generation
- dashboard data access
- report generation
- automation routes
- product UI routes

## Product Positioning

This repository is not intended as a tutorial scaffold.

It is positioned as:

- a portfolio-ready AI operations system
- a freelance demo for SME workflow automation
- a backend and automation case study
- a base for future deployment on a lightweight VPS

## Current Status

Implemented:

- workflow ingestion and extraction
- order and document generation
- follow-up task automation
- operator UI
- daily reporting and n8n-ready automation
- Docker packaging

Not yet implemented:

- production authentication and user accounts
- PostgreSQL deployment profile
- PDF invoice rendering
- background job scheduling inside the app
- advanced analytics and audit dashboards
- production-grade secrets management

## Recommended Next Steps

- Add user authentication and role-based access
- Move persistence to PostgreSQL for hosted deployment
- Add file storage or PDF export for invoices
- Add a deployment manifest or `docker-compose.yml`
- Finalize project docs in `docs/` for architecture and portfolio case study
