"""Command-line demo scenarios for the FoodBridge MVP."""

from __future__ import annotations

import json
from pathlib import Path

from foodbridge_agent.evals import run_fixture


SCENARIOS = {
    "happy_path": "safe_donation_happy_path.json",
    "unsafe_food": "unsafe_food_rejection.json",
    "prompt_injection": "prompt_injection_donor_notes.json",
    "resume_pending": "resume_approval_pending.json",
}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run a FoodBridge demo scenario.")
    parser.add_argument("scenario", choices=sorted(SCENARIOS))
    args = parser.parse_args()

    fixture_path = Path(__file__).resolve().parents[1] / "evals" / "fixtures" / SCENARIOS[args.scenario]
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    result = run_fixture(fixture)

    print(f"Scenario: {args.scenario}")
    print(f"Final state: {result.final_state}")
    print(f"Safety status: {result.safety_status}")
    print(f"Selected recipient: {result.selected_recipient_id}")
    print(f"Tool calls: {', '.join(result.tool_calls) or '(none)'}")
    print(f"Trace events: {', '.join(result.trace_events)}")
    if result.reasons:
        print("Reasons:")
        for reason in result.reasons:
            print(f"- {reason}")
    if result.questions:
        print("Questions:")
        for question in result.questions:
            print(f"- {question}")
    if result.draft_message:
        print("Draft message:")
        print(result.draft_message)


if __name__ == "__main__":
    main()

