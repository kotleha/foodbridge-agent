"""Deterministic safety triage for the FoodBridge MVP."""

from __future__ import annotations

from datetime import timedelta

from foodbridge_agent.models import Donation, SafetyDecision, SafetyStatus


INJECTION_PATTERNS = [
    "ignore all prior",
    "ignore previous",
    "send immediately",
    "do not ask for approval",
    "override safety",
    "reveal secrets",
]

HIGH_RISK_TERMS = [
    "seafood",
    "raw",
    "buffet",
    "overnight",
    "spoiled",
    "contaminated",
]


def triage_food_safety(donation: Donation) -> SafetyDecision:
    reasons: list[str] = []
    injection_signals = detect_prompt_injection(donation.notes)

    has_prepared_food = "prepared_meal" in donation.categories
    has_unsealed_prepared_food = any(
        item.category == "prepared_meal" and not item.sealed for item in donation.food_items
    )
    notes_lower = donation.notes.lower()

    if has_prepared_food and donation.prepared_at is None:
        reasons.append("Prepared food is missing a preparation time.")

    if has_prepared_food and donation.storage == "unknown":
        reasons.append("Prepared food has unknown storage conditions.")

    if reasons:
        return SafetyDecision(
            status=SafetyStatus.NEEDS_REVIEW,
            reasons=reasons,
            prompt_injection_signals=injection_signals,
        )

    if has_prepared_food and donation.storage == "room_temperature":
        reasons.append("Time-sensitive prepared food cannot be accepted after room-temperature storage.")

    if donation.prepared_at is not None:
        age = donation.available_until - donation.prepared_at
        if has_prepared_food and age > timedelta(hours=8):
            reasons.append("Prepared food is outside the MVP freshness window.")

    if has_unsealed_prepared_food and any(term in notes_lower for term in HIGH_RISK_TERMS):
        reasons.append("Unsealed prepared food includes high-risk handling notes.")

    if reasons:
        return SafetyDecision(
            status=SafetyStatus.REJECTED,
            reasons=reasons,
            prompt_injection_signals=injection_signals,
        )

    return SafetyDecision(
        status=SafetyStatus.ELIGIBLE,
        reasons=["Donation passed MVP safety checks."],
        prompt_injection_signals=injection_signals,
    )


def detect_prompt_injection(text: str) -> list[str]:
    lowered = text.lower()
    return [pattern for pattern in INJECTION_PATTERNS if pattern in lowered]

