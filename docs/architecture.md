# FoodBridge Architecture

## Current Runnable Baseline

```mermaid
flowchart TD
    user[User or Demo Fixture]
    cli[CLI Demo]
    api[FastAPI Demo Shell]
    workflow[Deterministic Workflow Runner]
    safety[Safety Triage]
    recipients[Recipient Matching]
    data[Seed Recipient Directory]
    approvals[Approval Gate]
    store[SQLite Store]
    evals[Eval Fixtures]

    user --> cli
    user --> api
    cli --> workflow
    api --> workflow
    evals --> workflow
    workflow --> safety
    workflow --> recipients
    recipients --> data
    workflow --> approvals
    api --> store
    workflow --> store
```

The current baseline is intentionally deterministic. It lets judges run the workflow, tests, and evals without credentials or live services.

## Agentic Target Architecture

```mermaid
flowchart TD
    user[Donor or Operator]
    ui[FastAPI UI]
    adk[ADK Root Agent]
    skill[food-safety Agent Skill]
    tools[Typed Tool Wrappers]
    mcp[Recipient Directory MCP Server]
    policy[Permission Policy]
    sqlite[SQLite State and Trace Store]
    evals[Eval Runner]

    user --> ui
    ui --> adk
    adk --> skill
    adk --> tools
    tools --> mcp
    tools --> policy
    tools --> sqlite
    evals --> tools
    evals --> policy
```

## Key Boundaries

- The model proposes actions; application code validates and executes them.
- Food safety triage must happen before recipient matching.
- Donor notes and recipient records are untrusted data.
- Dispatch communication is draft-first and approval-gated.
- SQLite stores workflow state and trace events outside the model context.
- MCP is used for recipient directory access, not broad arbitrary API access.

## Main Flow

1. Donation intake is received from CLI, API, or future UI.
2. Safety triage returns `eligible`, `needs_review`, or `rejected`.
3. Eligible donations search and rank recipients.
4. FoodBridge drafts a dispatch message.
5. Human approval is required before scheduling.
6. Approval resolution updates persisted state to `SCHEDULED` or `CANCELLED`.
7. Trace events record the workflow path.

## Safety Flow

```mermaid
flowchart TD
    intake[Donation Intake]
    injection[Prompt Injection Scan]
    safety[Food Safety Rules]
    reject[REJECTED_UNSAFE]
    review[NEEDS_MORE_INFO]
    eligible[ELIGIBLE_FOR_MATCHING]
    match[Recipient Matching]

    intake --> injection
    injection --> safety
    safety --> reject
    safety --> review
    safety --> eligible
    eligible --> match
```

## Pause And Resume Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Store
    participant Workflow

    User->>API: Submit donation
    API->>Workflow: Run intake
    Workflow->>Store: Save APPROVAL_PENDING
    API-->>User: Approval preview
    User->>API: Approve dispatch
    API->>Store: Resolve approval
    Store-->>API: SCHEDULED snapshot
    API-->>User: Scheduled dispatch summary
```

## Demo-Relevant Course Concepts

- ADK root agent: `foodbridge_agent/adk_agent.py`.
- MCP server: `mcp_servers/recipient_directory/server.py`.
- Agent Skill: `skills/food-safety/`.
- Security: prompt-injection detection, safety triage, approval gate, no real external sends.
- Evals: `evals/fixtures/` and `foodbridge_agent/evals.py`.
- Deployability: FastAPI shell and deterministic local setup.

