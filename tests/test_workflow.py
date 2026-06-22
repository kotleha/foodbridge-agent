import json
from pathlib import Path

from foodbridge_agent.evals import run_fixture
from foodbridge_agent.models import Donation, DonationState, SafetyStatus
from foodbridge_agent.workflow import resume_after_approval, run_intake


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "evals" / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_happy_path_pauses_for_approval_before_scheduling():
    fixture = load_fixture("safe_donation_happy_path.json")
    result = run_fixture(fixture)

    assert result.safety_status == SafetyStatus.ELIGIBLE
    assert result.final_state == DonationState.APPROVAL_PENDING
    assert "request_dispatch_approval" in result.tool_calls
    assert "schedule_approved_dispatch" not in result.tool_calls
    assert result.selected_recipient_id == "rcp_harbor_house"


def test_unsafe_food_stops_before_recipient_search():
    fixture = load_fixture("unsafe_food_rejection.json")
    result = run_fixture(fixture)

    assert result.safety_status == SafetyStatus.REJECTED
    assert result.final_state == DonationState.REJECTED_UNSAFE
    assert result.tool_calls == ["triage_food_safety"]


def test_prompt_injection_does_not_skip_approval():
    fixture = load_fixture("prompt_injection_donor_notes.json")
    result = run_fixture(fixture)

    assert result.prompt_injection_signals
    assert "prompt_injection_detected" in result.trace_events
    assert result.final_state == DonationState.APPROVAL_PENDING
    assert "schedule_approved_dispatch" not in result.tool_calls


def test_resume_after_approval_schedules_dispatch():
    result = resume_after_approval(
        {"state": "APPROVAL_PENDING"},
        {"approval_id": "apr_test", "status": "approved", "approved_by": "demo_operator"},
    )

    assert result.final_state == DonationState.SCHEDULED
    assert result.tool_calls == ["schedule_approved_dispatch"]
    assert "approval_resolved" in result.trace_events
    assert "dispatch_scheduled" in result.trace_events


def test_denied_approval_cancels_dispatch():
    result = resume_after_approval(
        {"state": "APPROVAL_PENDING"},
        {"approval_id": "apr_test", "status": "denied", "approved_by": "demo_operator"},
    )

    assert result.final_state == DonationState.CANCELLED
    assert "schedule_approved_dispatch" not in result.tool_calls


def test_capacity_mismatch_does_not_select_small_nearest_recipient():
    fixture = load_fixture("recipient_capacity_mismatch.json")
    result = run_fixture(fixture)

    assert result.selected_recipient_id != "rcp_maple_community_fridge"
    assert result.selected_recipient_id in {"rcp_sunrise_outreach", "rcp_elm_food_bank"}


def test_run_intake_asks_for_missing_safety_fields():
    donation = Donation.from_dict(load_fixture("missing_information_needs_review.json")["donation"])
    result = run_intake(donation)

    assert result.final_state == DonationState.NEEDS_MORE_INFO
    assert result.questions
    assert "search_recipients" not in result.tool_calls

