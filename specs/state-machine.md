# FoodBridge State Machine

Status: Draft implementation contract

## States

| State | Meaning |
| --- | --- |
| `INTAKE_RECEIVED` | A donation intake was accepted and persisted. |
| `NEEDS_MORE_INFO` | Required safety or matching fields are missing. |
| `REJECTED_UNSAFE` | The donation is not eligible under MVP safety rules. |
| `ELIGIBLE_FOR_MATCHING` | The donation passed safety triage and can be matched. |
| `MATCHING_RECIPIENTS` | Recipient search and ranking are in progress. |
| `MATCHED` | A recipient candidate has been selected and a plan can be drafted. |
| `APPROVAL_PENDING` | A dispatch message exists and waits for human approval. |
| `APPROVED` | The human approved the dispatch action. |
| `SCHEDULED` | The simulated dispatch was scheduled. |
| `COMPLETED` | The workflow is complete. |
| `CANCELLED` | The workflow was cancelled by the user or system. |
| `ERROR_NEEDS_REVIEW` | A tool, policy, or state error requires human review. |

## Allowed Transitions

| From | To | Required Condition |
| --- | --- | --- |
| `INTAKE_RECEIVED` | `NEEDS_MORE_INFO` | Safety triage cannot proceed without required fields. |
| `INTAKE_RECEIVED` | `REJECTED_UNSAFE` | Safety triage rejects the donation. |
| `INTAKE_RECEIVED` | `ELIGIBLE_FOR_MATCHING` | Safety triage marks the donation eligible. |
| `ELIGIBLE_FOR_MATCHING` | `MATCHING_RECIPIENTS` | Recipient search begins. |
| `MATCHING_RECIPIENTS` | `MATCHED` | At least one eligible recipient is ranked. |
| `MATCHING_RECIPIENTS` | `NEEDS_MORE_INFO` | Matching requires missing operational details. |
| `MATCHING_RECIPIENTS` | `ERROR_NEEDS_REVIEW` | Search or ranking fails unexpectedly. |
| `MATCHED` | `APPROVAL_PENDING` | Draft dispatch message and approval request are created. |
| `APPROVAL_PENDING` | `APPROVED` | Human approval is recorded. |
| `APPROVAL_PENDING` | `CANCELLED` | Human denies or cancels the dispatch. |
| `APPROVED` | `SCHEDULED` | Approved dispatch is scheduled. |
| `SCHEDULED` | `COMPLETED` | Demo workflow is finalized. |
| Any non-terminal state | `CANCELLED` | User cancels the workflow. |
| Any non-terminal state | `ERROR_NEEDS_REVIEW` | Tool, policy, or persistence error requires review. |

## Terminal States

- `REJECTED_UNSAFE`
- `COMPLETED`
- `CANCELLED`
- `ERROR_NEEDS_REVIEW`

## Invariants

- `REJECTED_UNSAFE` must not transition to any recipient-matching state.
- `SCHEDULED` requires an approved approval record.
- `COMPLETED` requires `SCHEDULED`.
- `schedule_approved_dispatch` must fail without approval.
- Prompt-injection detection must not grant permission or skip approval.
- Every transition must write a trace event.

## Trace Event Requirements

Each transition should record:

- previous state;
- next state;
- donation id;
- dispatch id when available;
- trigger event;
- relevant tool name when available;
- permission decision when available;
- short summary.

