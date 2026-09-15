# IT CareerPilot Backend

FastAPI backend for the IT CareerPilot IRS project.

## What is included

- Health check endpoint
- Resume parsing endpoint with a simple text-based parser
- Job analysis endpoint with requirement extraction
- Recommendation endpoint with hard-constraint checks and explainable scoring
- Focused pytest tests for the initial API contract

## Project layout

```text
backend/
  app/
    api/v1/          # HTTP routes
    core/            # settings and shared config
    matching/        # scoring and constraint logic
    parsers/         # resume and job parsing helpers
    schemas/         # Pydantic request/response models
    services/        # application use cases
    main.py          # FastAPI app factory
  tests/             # API and service tests
```

## Local setup

```bash
cd SystemCode/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app.main:app --reload
```

Open the interactive API docs at:

```text
http://127.0.0.1:8000/docs
```

## Run tests

```bash
pytest
```
