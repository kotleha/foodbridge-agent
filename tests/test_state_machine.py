import pytest

from foodbridge_agent.models import DonationState
from foodbridge_agent.state_machine import can_transition, require_transition


def test_expected_happy_path_transitions_are_allowed():
    path = [
        DonationState.INTAKE_RECEIVED,
        DonationState.ELIGIBLE_FOR_MATCHING,
        DonationState.MATCHING_RECIPIENTS,
        DonationState.MATCHED,
        DonationState.APPROVAL_PENDING,
        DonationState.APPROVED,
        DonationState.SCHEDULED,
        DonationState.COMPLETED,
    ]

    for current, next_state in zip(path, path[1:]):
        assert can_transition(current, next_state)


def test_rejected_unsafe_is_terminal():
    assert not can_transition(DonationState.REJECTED_UNSAFE, DonationState.MATCHING_RECIPIENTS)
    assert not can_transition(DonationState.REJECTED_UNSAFE, DonationState.APPROVAL_PENDING)


def test_invalid_transition_raises_clear_error():
    with pytest.raises(ValueError, match="Invalid transition"):
        require_transition(DonationState.INTAKE_RECEIVED, DonationState.SCHEDULED)

