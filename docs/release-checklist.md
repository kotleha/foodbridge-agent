# FoodBridge Release Checklist

Use this checklist before publishing the repository or submitting the Kaggle Writeup.

## Required Local Verification

- [ ] Run `python3 -m pip install -e '.[web,dev]'` in a clean environment.
- [ ] Run `python3 scripts/verify_release.py`.
- [ ] Read `docs/judge-walkthrough.md` from top to bottom and confirm it matches the final repository state.
- [ ] Run `python3 -m foodbridge_agent.demo happy_path`.
- [ ] Start `uvicorn app.main:app --reload` and open `http://127.0.0.1:8000/`.
- [ ] Confirm the dashboard can show happy path, unsafe food, prompt injection, missing info, and capacity mismatch.
- [ ] Confirm approval buttons move a persisted happy-path dispatch to `SCHEDULED`.

## Course Concept Evidence

- [ ] `docs/course-concepts.md` lists at least three selected concepts.
- [ ] ADK-facing code is present in `foodbridge_agent/adk_agent.py` and `foodbridge_agent/tools.py`.
- [ ] MCP server code is present in `mcp_servers/recipient_directory/server.py`.
- [ ] Security behavior is present in code and eval fixtures.
- [ ] Agent Skill package is present in `skills/food-safety/`.
- [ ] Tests covering the selected concepts pass.

## Public Repository Hygiene

- [ ] `.codex-local/` is not included in the public repository.
- [ ] No `.env`, API key, OAuth token, service account, or private recipient data is included.
- [ ] No `*.sqlite`, `*.sqlite3`, `*.db`, `__pycache__/`, `.pytest_cache/`, `build/`, `dist/`, or `*.egg-info/` artifacts are included.
- [ ] README setup commands work from a fresh clone.
- [ ] `docs/judge-walkthrough.md` gives a reviewer a working 3-minute path through the project.
- [ ] `docs/kaggle-writeup.md` is under 2,500 words.

## Kaggle Submission Fields

- [ ] Track is set to `Agents for Good`.
- [ ] Title is `FoodBridge Agent: Multi-Agent Food Rescue Dispatch with ADK + MCP`.
- [ ] Subtitle explains approval-gated food rescue dispatch.
- [ ] Writeup describes problem, solution, architecture, implementation, evals, and limitations.
- [ ] Public project link points to the public repository or public demo.
- [ ] Public project link opens without login and does not expose local `.codex-local/` notes.
- [ ] Cover/card image `docs/assets/foodbridge-cover.png` is added.
- [ ] Media gallery contains `docs/assets/dashboard-happy-path.png`, `docs/assets/dashboard-injection-probe.png`, and `docs/assets/dashboard-mobile.png`.
- [ ] Brief demo video is uploaded if the Kaggle UI requires it.
- [ ] Submission links include the public repository and, if available, a public demo or video link.

## Final Stop Conditions

Do not submit until:

- [ ] `python3 scripts/verify_release.py` passes.
- [ ] The public repository can be cloned and run without private credentials.
- [ ] The Writeup explicitly names the selected code-demonstrated course concepts.
- [ ] The Kaggle form has all required media/link/card-image fields completed.
