# FoodBridge Setup Guide

## Baseline Setup

The baseline requires Python 3.12 or newer and no external service credentials.

Install local web and test dependencies:

```bash
python3 -m pip install -e '.[web,dev]'
```

Run evals:

```bash
python3 -m foodbridge_agent.evals
```

Run tests:

```bash
pytest
```

Run a CLI scenario:

```bash
python3 -m foodbridge_agent.demo happy_path
```

Run the full release verification:

```bash
python3 scripts/verify_release.py
```

For static checks only:

```bash
python3 scripts/verify_release.py --skip-runtime
```

## Web Demo Setup

If FastAPI and Uvicorn are installed:

```bash
uvicorn app.main:app --reload
```

Then open the dashboard:

```text
http://127.0.0.1:8000/
```

API docs are available at:

```text
http://127.0.0.1:8000/docs
```

Useful endpoints:

- `GET /health`
- `GET /api/scenarios`
- `GET /api/recipients`
- `POST /api/demo/happy_path?persist=true`
- `POST /api/demo/unsafe_food`
- `POST /api/demo/prompt_injection`
- `POST /api/donations?persist=true`
- `POST /api/approvals/{approval_id}`

Set a local SQLite path:

```bash
export FOODBRIDGE_DB_PATH=./foodbridge.sqlite
```

Runtime database files are ignored by git.

## Optional ADK/MCP Setup

The current repository keeps ADK and MCP optional so the deterministic demo remains easy to run.

Install optional agent dependencies when ready:

```bash
python3 -m pip install '.[agent]'
```

The ADK-facing skeleton lives at:

```text
foodbridge_agent/adk_agent.py
```

The MCP adapter lives at:

```text
mcp_servers/recipient_directory/server.py
```

## No-Secrets Rule

Do not commit:

- API keys;
- OAuth tokens;
- service account files;
- real recipient contact data;
- real donor private data;
- local `.env` files;
- local SQLite runtime files.
