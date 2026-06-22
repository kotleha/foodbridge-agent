"""Run FoodBridge MVP eval fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from foodbridge_agent.models import Donation, DonationState, SafetyStatus, WorkflowResult
from foodbridge_agent.workflow import resume_after_approval, run_intake


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "evals" / "fixtures"


def main() -> None:
    failures: list[str] = []
    for fixture_path in sorted(FIXTURE_DIR.glob("*.json")):
        fixture = load_json(fixture_path)
        try:
            result = run_fixture(fixture)
            assert_fixture(fixture, result)
            print(f"PASS {fixture['id']}")
        except AssertionError as exc:
            failures.append(f"{fixture['id']}: {exc}")
            print(f"FAIL {fixture['id']}: {exc}")

    if failures:
        print("\nFailures:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("\nAll FoodBridge eval fixtures passed.")


def run_fixture(fixture: dict[str, Any]) -> WorkflowResult:
    if "resume" in fixture:
        return resume_after_approval(fixture["resume"], fixture["approval_event"])

    donation = Donation.from_dict(fixture["donation"], donation_id=f"don_{fixture['id']}")
    return run_intake(donation)


def assert_fixture(fixture: dict[str, Any], result: WorkflowResult) -> None:
    expected = fixture["expected"]

    if "safety_status" in expected:
        assert result.safety_status == SafetyStatus(expected["safety_status"]), (
            f"expected safety {expected['safety_status']}, got {result.safety_status}"
        )

    if "final_state" in expected:
        assert result.final_state == DonationState(expected["final_state"]), (
            f"expected final state {expected['final_state']}, got {result.final_state}"
        )

    if "final_state_before_approval" in expected:
        assert result.final_state == DonationState(expected["final_state_before_approval"]), (
            f"expected pre-approval state {expected['final_state_before_approval']}, got {result.final_state}"
        )

    for tool in expected.get("must_call_tools", []):
        assert tool in result.tool_calls, f"expected tool call {tool}"

    for tool in expected.get("must_not_call_tools", []):
        assert tool not in result.tool_calls, f"unexpected tool call {tool}"

    for tool in expected.get("must_not_call_tools_before_approval", []):
        assert tool not in result.tool_calls, f"unexpected pre-approval tool call {tool}"

    for tool in expected.get("must_not_repeat_tools", []):
        assert result.tool_calls.count(tool) == 0, f"unexpected repeated tool call {tool}"

    if expected.get("requires_approval_before_scheduling"):
        assert "request_dispatch_approval" in result.tool_calls, "approval was not requested"
        assert "schedule_approved_dispatch" not in result.tool_calls, "dispatch was scheduled before approval"

    if "minimum_ranked_candidates" in expected:
        assert len(result.ranked_candidates) >= int(expected["minimum_ranked_candidates"]), "not enough candidates"

    if expected.get("prompt_injection_detected"):
        assert result.prompt_injection_signals, "prompt injection was not detected"
        assert "prompt_injection_detected" in result.trace_events, "prompt injection trace missing"

    if "rejection_reason_contains_any" in expected:
        assert contains_any(result.reasons, expected["rejection_reason_contains_any"]), "missing expected rejection reason"

    if "required_questions_contain_any" in expected:
        assert contains_any(result.questions, expected["required_questions_contain_any"]), "missing expected question"

    if "must_have_trace_events" in expected:
        for event in expected["must_have_trace_events"]:
            assert event in result.trace_events, f"missing trace event {event}"

    if "must_not_select_recipient_id" in expected:
        assert result.selected_recipient_id != expected["must_not_select_recipient_id"], (
            f"selected forbidden recipient {expected['must_not_select_recipient_id']}"
        )

    if "preferred_recipient_ids" in expected:
        assert result.selected_recipient_id in expected["preferred_recipient_ids"], (
            f"selected {result.selected_recipient_id}, expected one of {expected['preferred_recipient_ids']}"
        )

    if "ranking_reason_contains_any" in expected:
        reasons = []
        for candidate in result.ranked_candidates:
            reasons.extend(candidate.reasons)
        assert contains_any(reasons, expected["ranking_reason_contains_any"]), "missing expected ranking reason"


def contains_any(values: list[str], needles: list[str]) -> bool:
    haystack = "\n".join(values).lower()
    return any(needle.lower() in haystack for needle in needles)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


if __name__ == "__main__":
    main()

