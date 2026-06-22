"""State transition rules for FoodBridge workflows."""

from __future__ import annotations

from foodbridge_agent.models import DonationState


ALLOWED_TRANSITIONS: dict[DonationState, set[DonationState]] = {
    DonationState.INTAKE_RECEIVED: {
        DonationState.NEEDS_MORE_INFO,
        DonationState.REJECTED_UNSAFE,
        DonationState.ELIGIBLE_FOR_MATCHING,
        DonationState.CANCELLED,
        DonationState.ERROR_NEEDS_REVIEW,
    },
    DonationState.ELIGIBLE_FOR_MATCHING: {
        DonationState.MATCHING_RECIPIENTS,
        DonationState.CANCELLED,
        DonationState.ERROR_NEEDS_REVIEW,
    },
    DonationState.MATCHING_RECIPIENTS: {
        DonationState.MATCHED,
        DonationState.NEEDS_MORE_INFO,
        DonationState.CANCELLED,
        DonationState.ERROR_NEEDS_REVIEW,
    },
    DonationState.MATCHED: {
        DonationState.APPROVAL_PENDING,
        DonationState.CANCELLED,
        DonationState.ERROR_NEEDS_REVIEW,
    },
    DonationState.APPROVAL_PENDING: {
        DonationState.APPROVED,
        DonationState.CANCELLED,
        DonationState.ERROR_NEEDS_REVIEW,
    },
    DonationState.APPROVED: {
        DonationState.SCHEDULED,
        DonationState.CANCELLED,
        DonationState.ERROR_NEEDS_REVIEW,
    },
    DonationState.SCHEDULED: {
        DonationState.COMPLETED,
        DonationState.ERROR_NEEDS_REVIEW,
    },
    DonationState.NEEDS_MORE_INFO: {
        DonationState.INTAKE_RECEIVED,
        DonationState.CANCELLED,
        DonationState.ERROR_NEEDS_REVIEW,
    },
    DonationState.REJECTED_UNSAFE: set(),
    DonationState.COMPLETED: set(),
    DonationState.CANCELLED: set(),
    DonationState.ERROR_NEEDS_REVIEW: set(),
}


def can_transition(current: DonationState, next_state: DonationState) -> bool:
    return next_state in ALLOWED_TRANSITIONS.get(current, set())


def require_transition(current: DonationState, next_state: DonationState) -> None:
    if not can_transition(current, next_state):
        raise ValueError(f"Invalid transition: {current} -> {next_state}")

