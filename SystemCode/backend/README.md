# IT CareerPilot Backend

FastAPI backend for the IT CareerPilot IRS project.

## What is included

- Health check endpoint
- Resume PDF parsing endpoint (`POST /api/v1/resumes/parse-pdf`, LLM-based)
- User profile and job-search constraints (`GET/PUT /api/v1/profile`, in-memory, single local user)
- Job analysis endpoint with requirement extraction
- Job sync/list endpoints backed by local SQLite storage
- Recommendation endpoint with hard-constraint checks and explainable scoring
- MIND Tech Skills Ontology snapshot loaded at application startup
- Focused pytest tests for the initial API contract

## Project layout

```text
backend/
  app/
    api/v1/          # HTTP routes
    core/            # settings and shared config
    db/              # SQLite connection and schema
    ingestion/       # external job source clients and synchronization
    knowledge/       # MIND knowledge graph loader
    matching/        # scoring and constraint logic
    parsers/         # resume and job parsing helpers
    repositories/    # persistence access
    schemas/         # Pydantic request/response models
    services/        # application use cases
    main.py          # FastAPI app factory
  tests/             # API and service tests
  data/              # versioned ontology data and ignored runtime databases
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

Use `POST /api/v1/jobs/sync` to fetch supported public job sources into the
local SQLite database. Use `GET /api/v1/jobs` to list active jobs and
`POST /api/v1/jobs/{job_id}/analyze-requirements` to create a structured JD.

Use `POST /api/v1/matches/skills` to calculate the implemented skill-score
components from a formatted resume and a structured JD. See
[`docs/skill-matching-score.md`](docs/skill-matching-score.md) for the formula.

Use `POST /api/v1/rules-screening` with a `UserProfile` body to run the
hard-constraint rule engine over all analysed jobs; it returns the jobs that
passed as `JobRequirementDocument`s plus per-rule rejection counts. Use
`POST /api/v1/ranking` with the same body to run the rule engine and then score
every passed job with `POST /api/v1/matches/skills`, sorted by `partial_score`.
See [`app/rule_engine/README.md`](app/rule_engine/README.md) for the rules.
Runtime database files such as `data/careerpilot.db` are ignored by Git.

## MIND knowledge graph

The backend includes a pinned MIND Tech Skills Ontology snapshot under
`data/mind_ontology`. The application validates and loads 3,333 skill nodes and
974 concept nodes during startup. Access the graph from application code with:

```python
from app.knowledge import get_mind_knowledge_graph

graph = get_mind_knowledge_graph()
react = graph.get_skill("react.js")
prerequisites = graph.related_skills("Next.js", "impliesKnowingSkills")
```

The graph is loaded and queryable but is not yet connected to recommendation
scoring.

## Run tests

```bash
pytest
```
