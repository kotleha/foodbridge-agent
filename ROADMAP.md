# FoodBridge Agent Roadmap

Status: active implementation plan
Last updated: 2026-06-22

## North Star

Build a polished, reproducible Kaggle Capstone submission that can credibly compete in the Agents for Good track.

The project should prove three things:

1. FoodBridge solves a real coordination problem with clear social value.
2. The agent is not a chatbot wrapper; it uses a harness, tools, MCP, state, approvals, safety, and evals.
3. Judges can run, inspect, and understand the project quickly.

## Rubric Alignment

### Pitch: 30 Points

- Core concept and value: make the food-waste and food-access problem obvious in the first 30 seconds.
- Writeup: explain architecture, course concepts, build journey, and limitations clearly.

### Implementation: 70 Points

- Technical implementation: ADK-facing agent structure, MCP adapter, state machine, tools, approval policy, safety checks, evals.
- Documentation: README, diagrams, setup commands, demo commands, eval commands, no-secrets policy.

## Release Gates

### Gate 0: Spec Baseline

Required:

- `specs/mvp.md`
- `specs/state-machine.md`
- seed recipient data
- eval fixtures
- deterministic harness

Status: complete.

### Gate 1: Trustworthy Local Harness

Required:

- pytest tests around safety, state transitions, matching, approval, and fixtures;
- deterministic eval runner;
- CLI demo scenarios;
- README instructions validated from a clean shell.

Acceptance:

- `python3 -m foodbridge_agent.evals` passes.
- `pytest` passes.
- CLI demos run without external credentials.

### Gate 2: Agent Skill And Policy Layer

Required:

- `skills/food-safety/SKILL.md`;
- focused references for MVP safety rules and handling templates;
- skill activation notes and boundaries;
- README mentions the skill as a course concept.

Acceptance:

- Skill is Markdown-only and reviewable.
- Skill description is narrow enough to avoid broad activation.
- Safety rules in the skill match deterministic safety behavior.

### Gate 3: ADK And MCP Integration Layer

Required:

- ADK root-agent skeleton;
- typed tool wrappers around the deterministic harness;
- local recipient-directory MCP server;
- graceful dependency errors when ADK/MCP packages are not installed;
- setup instructions for optional ADK/MCP dependencies.

Acceptance:

- Existing dependency-light evals still pass.
- ADK/MCP code imports safely without installed optional dependencies.
- MCP server code is isolated and reproducible.

### Gate 4: Persistence And Resume

Required:

- SQLite state store;
- persisted donation, dispatch, approval, and trace events;
- resume command or endpoint for `APPROVAL_PENDING`;
- replayable trace summaries.

Acceptance:

- Approval-pending state can survive process restart.
- Scheduling without approval fails.
- Trace shows state transitions and approval events.

### Gate 5: Demo UI

Required:

- FastAPI app;
- donation intake page or API;
- state timeline;
- safety panel;
- recipient ranking cards;
- draft message preview;
- approval controls;
- trace/debug drawer.

Acceptance:

- One command starts the app locally.
- Happy path, unsafe food, and prompt injection are visible in the UI.
- No login or credentials are required for demo mode.

Status: complete.

### Gate 6: Submission Package

Required:

- architecture diagram;
- cover image;
- Kaggle Writeup under 2,500 words;
- code-first course concepts matrix;
- judge walkthrough;
- release checklist;
- public repository cleanup;
- no-secrets scan;
- final setup test.

Acceptance:

- A new user can run evals and demo from README.
- Writeup explicitly names at least three course concepts.
- `docs/course-concepts.md` maps selected concepts to code and tests.
- `docs/judge-walkthrough.md` gives reviewers a concise first path through the project.
- `docs/release-checklist.md` covers final submission checks.
- Project link is public and does not require login.

Status: in progress. Writeup, course concept matrix, judge walkthrough, release checklist, cover image, and dashboard screenshots exist; final public repository cleanup remains.

## Implementation Order

1. Finish tests for current deterministic harness.
2. Add food-safety Agent Skill.
3. Add ADK-facing agent skeleton and tool wrappers.
4. Add SQLite persistence and approval records.
5. Add FastAPI demo shell.
6. Add UI polish and screenshots.
7. Add diagrams, course concepts matrix, and writeup draft.
8. Run final verification pass.

## Current Constraints

- No real email/SMS/logistics integration in MVP.
- No secrets or private recipient data.
- ADK and MCP are optional dependencies until the integration layer is installed.
- Synthetic data must remain enough for all evals and demos.

## Quality Bar

- Every risky action is draft-first and approval-gated.
- External or donor-provided text is untrusted data.
- Every tool call has a structured output or structured error.
- Evals verify behavior and tool trajectory, not only final text.
- Documentation stays runnable, not aspirational.
