# FoodBridge Agent Execution Plan

Status: active
Last updated: 2026-06-22

## Verified Submission Target

Sources checked on 2026-06-22:

- https://www.kaggle.com/competitions/vibecoding-agents-capstone-project
- https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google

Current target:

- Track: Agents for Good.
- Deadline: 2026-07-06 23:59 PT.
- Required package: Kaggle Writeup, selected track, cover/media gallery, and public project link or GitHub repository.
- Required course-concept proof: at least three concepts. FoodBridge will demonstrate ADK-facing agent code, MCP server code, security/evals, and Agent Skill code.

## Strategy

FoodBridge should compete as a small but complete agentic system, not as a broad concept demo.

Judging story:

1. Social value is obvious: reduce edible food waste and route food to local organizations.
2. Agent behavior is visible: safety triage, tool calls, ranked matches, draft, approval pause, resume.
3. Risk controls are real: donor notes are untrusted, unsafe food is rejected, external communication is simulated and approval-gated.
4. Reproducibility is strong: no secrets, synthetic data, local evals, local API, local UI.

## Release Gates

### Gate 1: Verified Harness

Status: complete.

Acceptance:

- `pytest -q` passes.
- `python3 -m foodbridge_agent.evals` passes.
- `python3 scripts/verify_release.py` passes.
- CLI demos work without external credentials.

### Gate 2: Course Concept Surface

Status: complete for the selected code-demonstrated concepts.

Acceptance:

- ADK-facing root agent imports safely without optional dependencies.
- MCP recipient-directory server is isolated and reproducible.
- Food-safety Agent Skill exists with focused references.
- Security behavior is covered by eval fixtures.
- Concept coverage is summarized in `docs/course-concepts.md`.

### Gate 3: Demo UI

Status: complete.

Acceptance:

- One command starts FastAPI and the dashboard.
- Dashboard shows happy path, unsafe rejection, prompt-injection signal, missing info, and capacity ranking.
- Approval buttons resolve persisted approval-pending dispatches.
- UI can be used locally without credentials.

### Gate 4: Submission Package

Status: in progress.

Acceptance:

- `docs/kaggle-writeup.md` is under 2,500 words.
- `docs/course-concepts.md` maps selected concepts to code and tests.
- `docs/judge-walkthrough.md` gives reviewers a fast path through the project.
- `docs/release-checklist.md` covers final local and public-release checks.
- Architecture diagram and screenshots are ready.
- README setup is verified from a clean environment.
- No secrets, runtime DB, caches, or private local memory are included.

### Gate 5: Public Release

Status: pending.

Acceptance:

- Public GitHub repository is readable and runnable.
- Optional deployment notes are clear.
- Kaggle Writeup links to the repository.
- Cover image and media gallery assets are final.

## Implementation Backlog

Now:

- Add final architecture screenshot.
- Tighten writeup after final feature set is locked.
- Prepare a brief demo video only if required by the Kaggle submission form.

Next:

- Test optional `.[agent]` install path.

Later:

- Decide whether Cloud Run deployment adds enough value for the deadline.
- Add a no-secrets and clean-repo release checklist.
