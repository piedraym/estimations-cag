# Estimations CAG

AI-powered software estimation service that converts meeting transcriptions into detailed project budgets. Uses a **Cache Augmented Generation (CAG)** architecture: a set of reference estimations is injected into the system prompt so the LLM produces structured, consistently-formatted outputs.

## How it works

1. You send a meeting transcription via the REST API
2. The service builds a prompt that includes 3 reference estimations as examples
3. The LLM (OpenAI or Anthropic) generates a structured estimation in markdown
4. The response includes the estimation, the model used, and token consumption

## Tech stack

- **Python 3.11+**
- **FastAPI** — REST API framework
- **Pydantic** — request/response validation
- **structlog** — structured logging
- **uv** — dependency management
- OpenAI and Anthropic SDKs

## Project structure

```
app/
├── main.py              # FastAPI app, middleware, lifespan
├── config.py            # Settings loaded from environment variables
├── routers/
│   └── estimations.py   # POST /api/v1/estimate endpoint
├── schemas/
│   └── estimation.py    # Request and response models
├── services/
│   └── llm_service.py   # LLM calls (OpenAI / Anthropic)
└── context/
    └── examples.py      # Reference estimations injected into the system prompt
```

## Setup

**1. Clone and install dependencies**

```bash
git clone <repo-url>
cd estimations-cag
uv sync
```

**2. Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Required — choose one provider
LLM_PROVIDER=openai          # or anthropic
OPENAI_API_KEY=sk-...        # required if LLM_PROVIDER=openai
ANTHROPIC_API_KEY=sk-ant-... # required if LLM_PROVIDER=anthropic

# Model to use
LLM_MODEL=gpt-4o-mini        # e.g. gpt-4o, claude-sonnet-4-6

# App settings
APP_ENV=development           # development | staging | production
LOG_LEVEL=DEBUG               # DEBUG | INFO | WARNING | ERROR
```

**3. Run the server**

```bash
uv run uvicorn app.main:app --reload
```

API available at `http://localhost:8000`

## API

### `POST /api/v1/estimate`

Generates a software project estimation from a meeting transcription.

**Request**

```json
{
  "transcription": "Meeting text describing the project requirements (min 50 characters)"
}
```

**Response**

```json
{
  "estimation": "## Project Title\n\n### Task Breakdown\n...",
  "model": "gpt-4o-mini",
  "provider": "openai",
  "usage": {
    "input_tokens": 1240,
    "output_tokens": 610,
    "total_tokens": 1850
  }
}
```

**Example**

```bash
curl -X POST http://localhost:8000/api/v1/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "transcription": "The client needs a landing page with a contact form, HubSpot CRM integration, and a blog with a WYSIWYG editor. The design is ready in Figma. Deadline is 4 weeks."
  }'
```

### `GET /health`

Returns service health status.

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development"
}
```

### Interactive docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Estimation output format

The LLM always returns estimations in this structure:

- **Project title** (H2 heading)
- **Task breakdown table** — task name, hours, cost in EUR
- **Total hours and total cost**
- **Recommended team composition**
- **Estimated duration in weeks**

Rates used: developer at 62.50 EUR/h (500 EUR/day), designer at 50 EUR/h (400 EUR/day).
