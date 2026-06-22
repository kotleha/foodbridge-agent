# FoodBridge Agent

Submission-facing title: **FoodBridge Agent: Multi-Agent Food Rescue Dispatch with ADK + MCP**.

FoodBridge Agent is an approval-gated AI agent workflow for routing safe surplus food from restaurants, cafes, grocery stores, and events to nearby shelters or food banks.

This project is being built for the Kaggle AI Agents: Intensive Vibe Coding Capstone Project, targeting the Agents for Good track.

## Problem

Useful prepared food is often discarded because matching a donor to a nearby recipient requires fast triage, operational context, safety checks, communication, and follow-up. A generic chatbot can answer questions about donation. FoodBridge coordinates the workflow.

## MVP Demo

The core demo starts with a cafe closing for the night:

> Bluebird Cafe has 18 turkey sandwiches and 12 sealed garden salads, refrigerated and available until 8:30 PM.

FoodBridge Agent:

1. parses the donation intake;
2. checks MVP food-safety rules;
3. searches a local recipient directory exposed through an MCP adapter;
4. ranks suitable recipients;
5. drafts a dispatch message;
6. pauses for human approval;
7. resumes and schedules the simulated dispatch after approval.

## Three-Minute Judge Walkthrough

Start with `docs/judge-walkthrough.md` for the fastest review path. It maps the project to Kaggle course concepts, demo cases, commands, and submission assets.

Quick local check:

```bash
python3 -m pip install -e '.[web,dev]'
python3 scripts/verify_release.py
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/`, then run the Happy Path, Injection Probe, Unsafe Food, Missing Info, and Capacity Match scenarios from the dashboard.

## Course Concepts Demonstrated

FoodBridge uses a code-first concept strategy. The selected concepts are:

- Agent system with ADK-facing code: root-agent skeleton plus typed tool wrappers.
- MCP server code: local recipient-directory server with list, search, and detail tools.
- Security features in code: prompt-injection detection, safety triage, approval gate, state machine, persistence, and evals.
- Agent Skill in code: food-safety skill with focused references and tests.

More detail is in `docs/course-concepts.md`.

## Current Architecture

```text
User
  -> CLI demo or FastAPI dashboard
  -> deterministic FoodBridge harness
      -> safety triage
      -> recipient search and ranking
      -> dispatch drafting
      -> approval-gated scheduling
  -> SQLite state store
  -> eval fixtures

Optional agent layer:

User
  -> ADK root agent
      -> food-safety skill
      -> local recipient-directory MCP server
      -> typed tools and approval policy
  -> trace log
```

## Repository Map

- `specs/mvp.md`: project blueprint and implementation contract.
- `specs/state-machine.md`: state transition contract.
- `docs/architecture.md`: architecture diagrams and workflow boundaries.
- `docs/setup.md`: baseline, web, and optional ADK/MCP setup notes.
- `docs/course-concepts.md`: code-first mapping of selected course concepts.
- `docs/judge-walkthrough.md`: shortest review path for Kaggle judges and repository reviewers.
- `docs/kaggle-writeup.md`: final Kaggle Writeup text.
- `docs/release-checklist.md`: final pre-submission checklist.
- `docs/assets/`: cover image and dashboard screenshots for the submission media gallery.
- `data/seed_recipients.json`: synthetic recipient directory.
- `evals/fixtures/`: MVP eval cases.
- `foodbridge_agent/`: dependency-light deterministic harness.
- `foodbridge_agent/storage.py`: SQLite persistence for workflow state and trace events.
- `app/main.py`: FastAPI demo shell for scenarios, donation intake, and approval resolution.
- `app/static/`: local dashboard for recording and judge review.
- `mcp_servers/recipient_directory/server.py`: local MCP server adapter skeleton.
- `skills/food-safety/`: procedural food-safety skill with focused references.
- `docs/execution-plan.md`: release plan for the capstone package.

## Requirements

- Python 3.12 or newer.

The current deterministic harness uses only the Python standard library.

Install the local demo and test dependencies:

```bash
python3 -m pip install -e '.[web,dev]'
```

Optional agent dependencies for the ADK/MCP layer:

- `google-adk`
- `mcp`

Install optional agent dependencies when ready to run the ADK/MCP layer:

```bash
python3 -m pip install '.[agent]'
```

## Run Evals

```bash
python3 -m foodbridge_agent.evals
```

Expected result:

```text
PASS missing_information_needs_review
PASS prompt_injection_donor_notes
PASS recipient_capacity_mismatch
PASS resume_approval_pending
PASS safe_donation_happy_path
PASS unsafe_food_rejection

All FoodBridge eval fixtures passed.
```

## Run Tests

```bash
pytest
```

## Verify Release Readiness

Run the full local release check:

```bash
python3 scripts/verify_release.py
```

This verifies code-first course concept coverage, required docs, absence of common runtime artifacts, secret-like text patterns, tests, evals, and module compilation.

## Optional ADK/MCP Layer

The deterministic harness is the current reproducible baseline. The ADK-facing skeleton lives in `foodbridge_agent/adk_agent.py` and wraps structured tools from `foodbridge_agent/tools.py`.

The local recipient-directory MCP adapter lives in `mcp_servers/recipient_directory/server.py`. It uses the same synthetic recipient data as the evals, so tool behavior is reproducible.

## Persistence

`foodbridge_agent/storage.py` provides a small SQLite store for donation state, dispatch drafts, approvals, and trace events. Runtime database files are ignored by git.

Set `FOODBRIDGE_DB_PATH` to choose a local database path for the API.

## Run Local Dashboard

If FastAPI and Uvicorn are installed:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/
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

More setup detail is in `docs/setup.md`.

## Run Demo Scenarios

Happy path:

```bash
python3 -m foodbridge_agent.demo happy_path
```

Unsafe food rejection:

```bash
python3 -m foodbridge_agent.demo unsafe_food
```

Prompt-injection handling:

```bash
python3 -m foodbridge_agent.demo prompt_injection
```

Resume from approval pending:

```bash
python3 -m foodbridge_agent.demo resume_pending
```

## Safety Model

FoodBridge treats donor notes and recipient records as untrusted data. They cannot override safety policy, tool permissions, or approval requirements.

The MVP rejects unsafe food before recipient search, pauses before any simulated external communication, and does not include real email, SMS, payment, or logistics integrations.

## No Secrets

This repository should not contain API keys, passwords, private tokens, or real recipient contact data. Demo contacts use the reserved `example.test` domain.
