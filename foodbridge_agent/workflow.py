"""Deterministic MVP workflow used by demos and evals."""

from __future__ import annotations

from foodbridge_agent.models import Donation, DonationState, SafetyStatus, WorkflowResult
from foodbridge_agent.recipients import load_recipients, rank_recipient_matches, search_recipients
from foodbridge_agent.safety import triage_food_safety
from foodbridge_agent.state_machine import require_transition


def run_intake(donation: Donation) -> WorkflowResult:
    result = WorkflowResult(final_state=DonationState.INTAKE_RECEIVED)
    result.trace_events.append("donation_received")

    result.tool_calls.append("triage_food_safety")
    result.trace_events.append("safety_triage_started")
    safety = triage_food_safety(donation)
    result.safety_status = safety.status
    result.reasons.extend(safety.reasons)
    result.prompt_injection_signals.extend(safety.prompt_injection_signals)
    result.trace_events.append("safety_triage_completed")

    if safety.prompt_injection_signals:
        result.trace_events.append("prompt_injection_detected")

    if safety.status == SafetyStatus.NEEDS_REVIEW:
        transition(result, DonationState.NEEDS_MORE_INFO)
        result.questions.extend(build_missing_info_questions(donation))
        return result

    if safety.status == SafetyStatus.REJECTED:
        transition(result, DonationState.REJECTED_UNSAFE)
        return result

    transition(result, DonationState.ELIGIBLE_FOR_MATCHING)
    transition(result, DonationState.MATCHING_RECIPIENTS)

    result.tool_calls.append("search_recipients")
    result.trace_events.append("recipient_search_started")
    recipients = search_recipients(donation, load_recipients())
    result.trace_events.append("recipient_search_completed")

    if not recipients:
        transition(result, DonationState.NEEDS_MORE_INFO)
        result.questions.append("No eligible recipient was found. Should the search radius or recipient directory be expanded?")
        return result

    result.tool_calls.append("rank_recipient_matches")
    ranked = rank_recipient_matches(donation, recipients)
    result.ranked_candidates.extend(ranked)
    result.trace_events.append("match_ranked")
    selected = ranked[0]
    result.selected_recipient_id = selected.recipient.recipient_id
    transition(result, DonationState.MATCHED)

    result.tool_calls.append("draft_dispatch_message")
    result.draft_message = draft_dispatch_message(donation, selected.recipient.name)
    result.trace_events.append("dispatch_drafted")

    result.tool_calls.append("request_dispatch_approval")
    result.approval_id = build_approval_id(donation.donation_id)
    result.trace_events.append("approval_requested")
    transition(result, DonationState.APPROVAL_PENDING)
    return result


def resume_after_approval(resume_state: dict, approval_event: dict) -> WorkflowResult:
    current = DonationState(str(resume_state["state"]))
    result = WorkflowResult(final_state=current)
    result.approval_id = str(approval_event["approval_id"])

    if current != DonationState.APPROVAL_PENDING:
        transition(result, DonationState.ERROR_NEEDS_REVIEW)
        result.reasons.append("Resume flow expected APPROVAL_PENDING state.")
        return result

    if approval_event.get("status") != "approved":
        transition(result, DonationState.CANCELLED)
        result.trace_events.append("approval_resolved")
        result.reasons.append("Approval was not granted.")
        return result

    transition(result, DonationState.APPROVED)
    result.trace_events.append("approval_resolved")

    result.tool_calls.append("schedule_approved_dispatch")
    transition(result, DonationState.SCHEDULED)
    result.trace_events.append("dispatch_scheduled")
    return result


def transition(result: WorkflowResult, next_state: DonationState) -> None:
    require_transition(result.final_state, next_state)
    result.trace_events.append(f"state:{result.final_state}->{next_state}")
    result.final_state = next_state


def build_missing_info_questions(donation: Donation) -> list[str]:
    questions: list[str] = []
    if donation.prepared_at is None:
        questions.append("What time was the prepared food made?")
    if donation.storage == "unknown":
        questions.append("Was the prepared food refrigerated, frozen, or held at room temperature?")
    return questions or ["Can you provide the missing safety details for this donation?"]


def draft_dispatch_message(donation: Donation, recipient_name: str) -> str:
    item_summary = ", ".join(f"{item.quantity} {item.name}" for item in donation.food_items)
    return (
        f"Hello {recipient_name}, {donation.donor_name} has surplus food available: "
        f"{item_summary}. Pickup is available at {donation.pickup_address} until "
        f"{donation.available_until.isoformat(timespec='minutes')}. "
        "Please confirm whether you can accept this donation."
    )


def build_approval_id(donation_id: str) -> str:
    safe_id = "".join(char if char.isalnum() or char in {"_", "-"} else "_" for char in donation_id)
    return f"apr_dsp_{safe_id}"
