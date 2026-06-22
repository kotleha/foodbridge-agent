"""JSON-friendly serialization helpers for FoodBridge outputs."""

from __future__ import annotations

from foodbridge_agent.models import MatchCandidate, WorkflowResult


def workflow_result_to_dict(result: WorkflowResult) -> dict:
    return {
        "final_state": result.final_state.value,
        "safety_status": result.safety_status.value if result.safety_status else None,
        "reasons": result.reasons,
        "prompt_injection_signals": result.prompt_injection_signals,
        "selected_recipient_id": result.selected_recipient_id,
        "ranked_candidates": [match_candidate_to_dict(candidate) for candidate in result.ranked_candidates],
        "draft_message": result.draft_message,
        "approval_id": result.approval_id,
        "tool_calls": result.tool_calls,
        "trace_events": result.trace_events,
        "questions": result.questions,
    }


def match_candidate_to_dict(candidate: MatchCandidate) -> dict:
    return {
        "recipient_id": candidate.recipient.recipient_id,
        "name": candidate.recipient.name,
        "recipient_type": candidate.recipient.recipient_type,
        "score": candidate.score,
        "distance_miles_demo": candidate.recipient.distance_miles_demo,
        "capacity_meals": candidate.recipient.capacity_meals,
        "pickup_supported": candidate.recipient.pickup_supported,
        "reasons": candidate.reasons,
    }

