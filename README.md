# WhatsApp-to-Invoice AI Workflow System for SMEs

A lightweight, portfolio-ready AI automation project that turns customer messages into structured business actions such as quotations, invoices, follow-up tasks, and daily reports.

## Project Goal

This project is designed to demonstrate how to build a real AI business workflow system for:

- SME demos
- freelance clients
- AI engineer interviews
- backend and automation portfolios

The system will simulate a business flow like this:

Customer message -> AI extraction -> order or lead creation -> pricing -> invoice or quotation -> task creation -> dashboard update -> daily report

## Learning-First Build Strategy

This project is intentionally built checkpoint by checkpoint.

Rules for the build:

- one main concept per checkpoint
- minimal code only
- clear explanation before and after each change
- tests added alongside important functionality
- no move to the next checkpoint until the current one is understood and working

## Planned Stack

- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite first, PostgreSQL-ready structure later
- Pydantic and pydantic-settings
- pytest
- Jinja2 for invoice templates
- Streamlit for the dashboard
- SMTP and n8n for reporting and automation

## Initial Project Structure

```text
app/
  api/
    routes/
  ai/
    prompts/
    providers/
  core/
  models/
  repositories/
  schemas/
  services/
  templates/
  utils/
dashboard/
docs/
data/
n8n/
  workflow_examples/
tests/
```

## Folder Purpose

- `app/`: main backend application code
- `app/api/routes/`: FastAPI endpoints only
- `app/core/`: shared core setup such as config and database
- `app/models/`: SQLAlchemy database models
- `app/schemas/`: Pydantic request and response schemas
- `app/repositories/`: data access layer
- `app/services/`: business logic layer
- `app/ai/`: AI provider abstraction, prompts, and provider implementations
- `app/templates/`: invoice or quotation templates
- `app/utils/`: small helper utilities
- `dashboard/`: Streamlit demo dashboard
- `docs/`: architecture, decisions, learning log, and portfolio notes
- `data/`: sample seed files such as product catalogs
- `n8n/`: workflow examples for automation orchestration
- `tests/`: automated tests

## Planned Roadmap

1. Project foundation and environment setup
2. Database models, schemas, and seed data
3. AI message understanding engine
4. Order, pricing, and invoice generation
5. Task management and follow-up workflow
6. Streamlit dashboard
7. Daily report, email, and n8n integration

## Status

Current checkpoint: Task 1.1 - project folders and README
