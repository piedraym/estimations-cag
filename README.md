# Estimations CAG

AI-powered software estimation service that converts meeting transcriptions into detailed project budgets. Uses a **Cache Augmented Generation (CAG)** architecture: a set of reference estimations is injected into the system prompt so the LLM produces structured, consistently-formatted outputs.

## How it works

1. You send a meeting transcription plus typed parameters (project type, detail level, output format) via the REST API or the React form UI
2. The service renders a versioned Jinja2 prompt template that includes 3 reference estimations as examples
3. The request goes through **LiteLLM**, which calls the configured model (OpenAI or Anthropic) with automatic fallback to a secondary model if configured
4. Identical requests (same transcription + model) are served from a **Redis cache** (exact match) instead of calling the LLM again
5. The LLM generates a structured estimation in markdown, returned either as a single JSON response or streamed token-by-token via **SSE**
6. The response includes the estimation, the model used, the provider, the prompt version, and token consumption

## Tech stack

- **Python 3.11+**
- **FastAPI** — REST API framework
- **LiteLLM** — unified wrapper for OpenAI / Anthropic models, with fallback support
- **Redis** — exact-match response cache
- **sse-starlette** — Server-Sent Events for streaming responses
- **Jinja2** — versioned prompt templates
- **React (Vite)** — form-based UI, in `frontend/`
- **Pydantic** — request/response validation
- **structlog** — structured logging
- **uv** — Python dependency management

## Project structure

```
app/
├── main.py              # FastAPI app, middleware, lifespan, Redis cache setup
├── config.py            # Settings loaded from environment variables
├── routers/
│   └── estimations.py   # POST /api/v1/estimate and /api/v1/estimate/stream endpoints
├── schemas/
│   └── estimation.py    # Request and response models
├── services/
│   └── llm_service.py   # LLM calls via LiteLLM (sync + streaming, with caching)
└── prompts/
    ├── loader.py         # Renders versioned Jinja2 templates
    ├── examples.py       # Reference estimations injected into the system prompt
    └── estimation/v1/    # system.j2, user.j2, examples.j2
frontend/                 # React (Vite) form UI that consumes the API
```

## Required services

To run the project locally you need **three things running**:

| Service | Purpose | Default address |
| --- | --- | --- |
| Redis | Exact-match response cache used by LiteLLM | `localhost:6379` |
| FastAPI backend (uvicorn) | REST API (`/api/v1/estimate`, `/api/v1/estimate/stream`) | `http://localhost:8000` |
| React UI (Vite) | Form interface that calls the backend | `http://localhost:5173` |

If Redis is not running, the API still works, but every request is a cache miss (LiteLLM silently skips caching on connection errors).

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
# Required — at least one provider key, matching LLM_MODEL / LLM_FALLBACK_MODEL
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Model to use, format "<provider>/<model-name>"
LLM_MODEL=openai/gpt-4o-mini
# Optional fallback model, used if LLM_MODEL fails
LLM_FALLBACK_MODEL=anthropic/claude-haiku-4-5-20251001

# App settings
APP_ENV=development           # development | staging | production
LOG_LEVEL=DEBUG                # DEBUG | INFO | WARNING | ERROR

# Redis cache (exact match)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
CACHE_TTL_SECONDS=3600
```

**3. Start Redis**

```bash
brew install redis        # first time only
brew services start redis # keeps running across reboots
```

Alternatively, run it in the foreground without a background service:

```bash
redis-server
```

Check it's up with:

```bash
redis-cli ping   # -> PONG
```

**4. Run the API server**

```bash
uv run uvicorn app.main:app --reload
```

API available at `http://localhost:8000`

**5. Install and run the React UI** (in a separate terminal)

```bash
cd frontend
npm install
npm run dev
```

UI available at `http://localhost:5173`

## API

### `POST /api/v1/estimate`

Generates a software project estimation from a meeting transcription.

**Request**

```json
{
  "transcription": "Meeting text describing the project requirements (min 50 characters)",
  "project_type": "web_application",
  "detail_level": "detailed",
  "output_format": "phases_table"
}
```

`project_type` (`web_application` | `mobile_app` | `landing_page`), `detail_level` (`summary` | `medium` | `detailed`) and `output_format` (`phases_table` | `narrative`) are optional and default as shown above.

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
  },
  "prompt_version": "v1"
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

### `POST /api/v1/estimate/stream`

Same input as `/api/v1/estimate`, but streams the estimation as it's generated using Server-Sent Events. Each event's `data` field is a JSON-encoded text fragment (delta) to append to the response.

The response includes an `X-Cache-Hit` header (`"true"` or `"false"`) indicating whether the result came from the Redis cache. On a cache hit, the full estimation is sent as a single event.

**Example**

```bash
curl -N -X POST http://localhost:8000/api/v1/estimate/stream \
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

## Caching

LiteLLM is configured with a Redis-backed **exact-match cache** (`app/main.py`). For both `/api/v1/estimate` and `/api/v1/estimate/stream`, identical requests (same model + messages) within `CACHE_TTL_SECONDS` are served from Redis instead of calling the LLM provider again.

- Cache hits are returned immediately (no LLM call, no token usage).
- For the streaming endpoint, the `X-Cache-Hit` response header reports whether the cache was used.
- Caching fails silently if Redis is unreachable — the API keeps working, just without caching.

## React form UI

`frontend/` (React + Vite) provides a form-based interface backed by `/api/v1/estimate`:

- A form with a transcription textarea and three selects (project type, detail level, output format).
- The sidebar shows the model used and token usage (input/output/total) from the last response.

## Estimation output format

The LLM always returns estimations in this structure:

- **Project title** (H2 heading)
- **Task breakdown table** — task name, hours, cost in EUR
- **Total hours and total cost**
- **Recommended team composition**
- **Estimated duration in weeks**

Rates used: developer at 62.50 EUR/h (500 EUR/day), designer at 50 EUR/h (400 EUR/day).
