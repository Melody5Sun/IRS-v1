# IT CareerPilot Backend

FastAPI backend for the IT CareerPilot IRS project.

## What is included

- Health check endpoint
- Resume PDF parsing endpoint (`POST /api/v1/resumes/parse-pdf`, LLM-based)
- User profile and job-search constraints (`GET/PUT /api/v1/profile`, in-memory, single local user)
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
conda activate careerpilot-backend
cd SystemCode/backend
python -m pip install -r requirements.txt
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
