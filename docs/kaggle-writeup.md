# FoodBridge Agent: Multi-Agent Food Rescue Dispatch with ADK + MCP

Subtitle: approval-gated food rescue dispatch for the Agents for Good track.

## Summary

FoodBridge Agent is an AI agent workflow that helps route safe surplus food from restaurants, cafes, grocery stores, and events to nearby shelters or food banks.

The problem is operational, not conversational. Useful prepared food is often discarded because the pickup window is short and the operator must quickly decide whether the donation is safe, find a suitable recipient, check capacity, draft communication, and avoid unsafe or unauthorized action. A generic chatbot can answer questions about donation. FoodBridge coordinates the workflow with tools, state, approvals, and evals.

The MVP uses synthetic data and runs locally. A donor submits food details. The agent triages food safety, searches a local recipient directory, ranks matches, drafts a dispatch message, pauses for human approval, and resumes to mark the simulated dispatch as scheduled.

## Why Agents Help

Food rescue dispatch is a good agent use case because each decision depends on several pieces of context:

- donor intake details, including food category, quantity, storage, and pickup window;
- safety rules for prepared meals and incomplete handling information;
- recipient constraints, such as accepted categories, capacity, distance, and pickup support;
- communication drafting that must remain approval-gated;
- durable state, because a dispatch may pause and resume after approval.

FoodBridge is intentionally not a broad assistant. It is a narrow agentic workflow with explicit states, typed tools, local policy enforcement, and testable failure cases.

## Demo Flow

The main scenario starts with Bluebird Cafe offering 18 turkey sandwiches and 12 garden salads. The food is sealed, refrigerated, and available until 8:30 PM.

FoodBridge:

1. accepts the donation intake;
2. runs MVP food-safety checks;
3. searches a recipient directory through a local MCP server adapter;
4. ranks recipients by capacity, distance, pickup support, and accepted food categories;
5. drafts a recipient message;
6. pauses at `APPROVAL_PENDING`;
7. persists the approval record;
8. resumes after operator approval and records `SCHEDULED`.

The dashboard also shows negative and adversarial cases. Unsafe room-temperature prepared food is rejected before recipient search. Donor notes containing instructions such as "ignore prior rules" or "do not ask for approval" are recorded as prompt-injection signals, but they do not override safety policy or skip the approval gate.

## Course Concepts Demonstrated

FoodBridge uses a code-first strategy and demonstrates four course concepts, more than the required three.

Agent system with ADK-facing code:

- `foodbridge_agent/adk_agent.py` defines the root-agent instruction and optional ADK builder.
- `foodbridge_agent/tools.py` exposes narrow typed tool wrappers around the deterministic harness.
- ADK remains optional so the baseline project can run without cloud credentials.

MCP Server:

- `mcp_servers/recipient_directory/server.py` exposes `list_recipients`, `search_recipients`, and `get_recipient`.
- The MCP server uses the same synthetic recipient directory as the eval suite, so judging behavior is reproducible.
- `tests/test_mcp_server.py` verifies the server functions without requiring live external services.

Security features:

- Donor notes and recipient records are treated as untrusted data.
- Prompt-injection phrases are detected and traced.
- Unsafe food stops before recipient search or dispatch drafting.
- External communication is simulated and approval-gated.
- SQLite records donations, dispatches, approvals, and trace events.
- Evals verify happy path, unsafe rejection, prompt injection, missing information, capacity mismatch, and resume behavior.

Agent Skill:

- `skills/food-safety/SKILL.md` packages the food-safety workflow as a reusable Agent Skill.
- Focused references separate MVP safety rules from handling templates.
- `tests/test_agent_skill.py` verifies the skill metadata, references, and security boundaries.

The complete concept matrix is in `docs/course-concepts.md`.

## Technical Implementation

The core harness is dependency-light. The deterministic workflow in `foodbridge_agent/workflow.py` owns state transitions:

`INTAKE_RECEIVED -> ELIGIBLE_FOR_MATCHING -> MATCHING_RECIPIENTS -> MATCHED -> APPROVAL_PENDING -> APPROVED -> SCHEDULED`

Unsafe or incomplete cases stop earlier at `REJECTED_UNSAFE` or `NEEDS_MORE_INFO`.

Application code, not the model, enforces safety-sensitive behavior. The safety layer treats user-provided notes as untrusted. Recipient ranking is deterministic so tests and demo output remain stable. SQLite persistence stores workflow state and approval records so an approval-pending dispatch can survive restart.

The local web demo is served by FastAPI at `/`. It exposes scenario controls, donation intake, safety decisions, ranked recipients, draft message preview, approval controls, tool call path, and trace events. The same API powers tests and the dashboard.

## Evaluation And Verification

The eval suite covers:

- safe happy path;
- unsafe food rejection;
- prompt-injection attempt in donor notes;
- missing safety information;
- recipient capacity mismatch;
- resume from approval pending.

The tests verify state transitions, tool calls, approval behavior, persistence, API endpoints, MCP server functions, Agent Skill packaging, and optional ADK import behavior.

Run the release verifier:

```bash
python3 scripts/verify_release.py
```

The verifier checks code-first concept coverage, required docs, runtime artifact hygiene, secret-like text patterns, tests, evals, and module compilation.

## Reproducibility

FoodBridge requires Python 3.12 or newer. The repository uses synthetic data and no real recipient or donor records.

Setup:

```bash
python3 -m pip install -e '.[web,dev]'
python3 scripts/verify_release.py
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/
```

## Limitations And Next Steps

FoodBridge is not legal, medical, or food-safety authority software. The MVP uses conservative rules and synthetic data. It does not send real email or SMS, does not use real organization records, and does not perform production routing.

Production next steps would include reviewed local food donation policy, real organization onboarding, authenticated operator accounts, audited communications, geocoding and routing, rate limits, monitoring, and stronger human review for edge cases.

The goal of the MVP is to demonstrate a complete, inspectable agentic workflow for a real public-good coordination problem: safe food rescue with visible tools, state, approvals, and evals.
