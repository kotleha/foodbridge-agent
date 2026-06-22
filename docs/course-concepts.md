# Course Concepts Coverage

Status: code-first strategy
Last updated: 2026-06-22

FoodBridge demonstrates at least three Kaggle course concepts through repository code and tests. Media assets may still be required by the Kaggle submission form, but the concept evidence below is code-first and reproducible.

## Selected Concepts

| Concept | Where It Is Demonstrated | Verification |
| --- | --- | --- |
| Agent system with ADK | `foodbridge_agent/adk_agent.py`, `foodbridge_agent/tools.py` | `tests/test_adk_agent.py`, `tests/test_tools.py` |
| MCP Server | `mcp_servers/recipient_directory/server.py` | `tests/test_mcp_server.py` |
| Security features | `foodbridge_agent/safety.py`, `foodbridge_agent/state_machine.py`, `foodbridge_agent/storage.py`, `evals/fixtures/` | `tests/test_safety.py`, `tests/test_workflow.py`, `tests/test_storage.py`, `tests/test_eval_fixtures.py` |
| Agent Skills | `skills/food-safety/SKILL.md`, `skills/food-safety/references/` | `tests/test_agent_skill.py` |

## Not Used For Minimum Coverage

| Concept | Reason |
| --- | --- |
| Antigravity | The requirements table lists it as video-demonstrated. FoodBridge does not depend on it for the minimum three code-backed concepts. |
| Deployability | The requirements table lists it as video-demonstrated. FoodBridge still includes runnable setup and a FastAPI dashboard, but deployability is not counted as one of the selected three code-backed concepts. |

## Fast Reviewer Map

Use `docs/judge-walkthrough.md` for the shortest judge-facing path through the same evidence. It summarizes the title, concepts, commands, demo cases, and required submission assets.

## Verification Commands

```bash
pytest -q
python3 -m foodbridge_agent.evals
python3 -m compileall -q foodbridge_agent mcp_servers app tests
python3 scripts/verify_release.py
```

## Evidence Summary

ADK-facing code:

- `foodbridge_agent/adk_agent.py` defines the root-agent instruction and optional ADK builder.
- `foodbridge_agent/tools.py` exposes narrow typed tool wrappers around the deterministic harness.
- Optional ADK dependencies are guarded so the baseline project remains runnable.

MCP server code:

- `mcp_servers/recipient_directory/server.py` exposes `list_recipients`, `search_recipients`, and `get_recipient`.
- The server reads the same synthetic recipient directory used by evals.
- The MCP package is optional; deterministic functions remain testable without it.

Security features in code:

- Donor notes are treated as untrusted data.
- Prompt-injection phrases are detected and traced.
- Unsafe food stops before recipient search.
- External communication is simulated and approval-gated.
- Approval records and trace events are persisted in SQLite.

Agent Skill code:

- `skills/food-safety/SKILL.md` has Agent Skill frontmatter and procedural guidance.
- Focused references separate MVP rules and handling templates.
- The skill does not grant new tools or bypass approval policy.
