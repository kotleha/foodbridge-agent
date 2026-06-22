"""Recipient directory loading and matching logic."""

from __future__ import annotations

import json
from pathlib import Path

from foodbridge_agent.models import Donation, MatchCandidate, Recipient


DEFAULT_RECIPIENT_DATA = Path(__file__).resolve().parents[1] / "data" / "seed_recipients.json"


def load_recipients(path: Path = DEFAULT_RECIPIENT_DATA) -> list[Recipient]:
    with path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [Recipient.from_dict(item) for item in raw]


def search_recipients(donation: Donation, recipients: list[Recipient]) -> list[Recipient]:
    return [
        recipient
        for recipient in recipients
        if donation.categories.issubset(recipient.accepts_categories)
        and recipient.capacity_meals >= donation.total_quantity
    ]


def rank_recipient_matches(donation: Donation, recipients: list[Recipient]) -> list[MatchCandidate]:
    candidates: list[MatchCandidate] = []

    for recipient in recipients:
        score = 100.0
        reasons = []

        capacity_margin = recipient.capacity_meals - donation.total_quantity
        if capacity_margin >= 0:
            score += min(capacity_margin, 100) * 0.1
            reasons.append(f"Capacity can handle {donation.total_quantity} meals.")
        else:
            score -= 100
            reasons.append("Capacity is too small for this donation.")

        score -= recipient.distance_miles_demo * 4
        reasons.append(f"Demo distance is {recipient.distance_miles_demo:.1f} miles.")

        if recipient.pickup_supported:
            score += 8
            reasons.append("Recipient supports pickup coordination.")

        if "prepared_meal" in donation.categories:
            reasons.append("Recipient accepts prepared meals.")

        candidates.append(MatchCandidate(recipient=recipient, score=round(score, 2), reasons=reasons))

    return sorted(candidates, key=lambda candidate: candidate.score, reverse=True)

