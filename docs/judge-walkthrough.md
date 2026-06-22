# FoodBridge Judge Walkthrough

This is the shortest path for a Kaggle judge or reviewer to understand and run FoodBridge.

## One-Minute Summary

FoodBridge Agent is a production-style multi-agent food rescue dispatch workflow for the Agents for Good track. It routes safe surplus food from donors to nearby recipient organizations while enforcing safety checks, prompt-injection handling, recipient matching, approval gating, persistence, and eval coverage.

Submission-facing title:

```text
FoodBridge Agent: Multi-Agent Food Rescue Dispatch with ADK + MCP
```

## What To Look For First

1. **Real problem:** safe surplus food often expires before a donor can find a recipient, confirm capacity, draft outreach, and get approval.
2. **Agentic workflow:** the system performs safety triage, tool-backed recipient search, ranking, dispatch drafting, approval pause, and resume.
3. **Code-demonstrated concepts:** ADK-facing agent code, MCP server, security features, and Agent Skill packaging.
4. **Risk controls:** donor notes are untrusted, unsafe food stops early, prompt-injection attempts are traced, and no dispatch is scheduled without approval.
5. **Reproducibility:** synthetic data, local FastAPI dashboard, SQLite persistence, eval fixtures, and a release verifier.

## Course Concepts Evidence

| Concept | Primary Evidence | Verification |
| --- | --- | --- |
| Agent / Multi-agent system with ADK-facing code | `foodbridge_agent/adk_agent.py`, `foodbridge_agent/tools.py` | `tests/test_adk_agent.py`, `tests/test_tools.py` |
| MCP Server | `mcp_servers/recipient_directory/server.py` | `tests/test_mcp_server.py` |
| Security features | `foodbridge_agent/safety.py`, `foodbridge_agent/state_machine.py`, `foodbridge_agent/storage.py`, `evals/fixtures/` | `tests/test_safety.py`, `tests/test_workflow.py`, `tests/test_storage.py`, `tests/test_eval_fixtures.py` |
| Agent Skill | `skills/food-safety/SKILL.md`, `skills/food-safety/references/` | `tests/test_agent_skill.py` |

## Three-Minute Local Run

Install:

```bash
python3 -m pip install -e '.[web,dev]'
```

Run the full release verifier:

```bash
python3 scripts/verify_release.py
```

Run a CLI scenario:

```bash
python3 -m foodbridge_agent.demo happy_path
```

Start the dashboard:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/
```

## Demo Cases

- `Happy Path`: eligible refrigerated donation, ranked recipient match, draft dispatch, approval pending.
- `Unsafe Food`: room-temperature prepared food is rejected before recipient search.
- `Injection Probe`: donor note attempts to override policy; the signal is traced and approval remains required.
- `Missing Info`: incomplete safety details stop the workflow for review.
- `Capacity Match`: recipient ranking exposes capacity and fit constraints.

## Architecture Snapshot

```text
Donor or Operator
  -> FastAPI dashboard or CLI
  -> FoodBridge harness
      -> safety triage
      -> recipient matching through MCP-facing directory tools
      -> dispatch draft
      -> approval gate
      -> persisted pause/resume state
  -> eval fixtures and trace events
```

## Submission Assets To Include

- Kaggle Writeup text from `docs/kaggle-writeup.md`.
- Public repository link with this walkthrough and README.
- Dashboard screenshots from `docs/assets/dashboard-happy-path.png`, `docs/assets/dashboard-injection-probe.png`, and `docs/assets/dashboard-mobile.png`.
- Cover/card image from `docs/assets/foodbridge-cover.png`.
- Brief demo video if the Kaggle submission form requires media upload.

## Reviewer Notes

FoodBridge intentionally avoids live email, SMS, payment, maps, and real recipient records in the MVP. Those would create unnecessary risk for a capstone demo. The useful behavior is the inspectable agent workflow: state, tools, safety, approvals, persistence, and evals.
