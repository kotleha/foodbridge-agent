# FoodBridge Eval Fixtures

These fixtures define the MVP evaluation set for FoodBridge Agent.

The evals are designed to test the harness, not only the final natural-language answer. A passing implementation should satisfy expected state transitions, tool-call constraints, permission checks, and safety outcomes.

## Fixture Shape

Each fixture contains:

- `id`: stable eval identifier.
- `description`: human-readable test purpose.
- `donation`: input donation payload.
- `resume`: optional saved state for resume tests.
- `expected`: required behavioral assertions.

## MVP Eval Coverage

- Safe donation happy path.
- Unsafe food rejection.
- Prompt injection in donor notes.
- Missing information flow.
- Resume from approval pending.
- Recipient capacity mismatch.

