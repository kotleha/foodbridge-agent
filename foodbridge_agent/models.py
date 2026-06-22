"""Core data models for the FoodBridge MVP harness."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class DonationState(StrEnum):
    INTAKE_RECEIVED = "INTAKE_RECEIVED"
    NEEDS_MORE_INFO = "NEEDS_MORE_INFO"
    REJECTED_UNSAFE = "REJECTED_UNSAFE"
    ELIGIBLE_FOR_MATCHING = "ELIGIBLE_FOR_MATCHING"
    MATCHING_RECIPIENTS = "MATCHING_RECIPIENTS"
    MATCHED = "MATCHED"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ERROR_NEEDS_REVIEW = "ERROR_NEEDS_REVIEW"


class SafetyStatus(StrEnum):
    ELIGIBLE = "eligible"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


@dataclass(frozen=True)
class FoodItem:
    name: str
    quantity: int
    category: str
    sealed: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FoodItem":
        return cls(
            name=str(data["name"]),
            quantity=int(data["quantity"]),
            category=str(data["category"]),
            sealed=bool(data["sealed"]),
        )


@dataclass(frozen=True)
class Donation:
    donor_name: str
    donor_contact: str | None
    pickup_address: str
    food_items: list[FoodItem]
    prepared_at: datetime | None
    available_until: datetime
    storage: str
    notes: str
    donation_id: str = "don_demo"

    @property
    def total_quantity(self) -> int:
        return sum(item.quantity for item in self.food_items)

    @property
    def categories(self) -> set[str]:
        return {item.category for item in self.food_items}

    @classmethod
    def from_dict(cls, data: dict[str, Any], donation_id: str = "don_demo") -> "Donation":
        return cls(
            donation_id=donation_id,
            donor_name=str(data["donor_name"]),
            donor_contact=data.get("donor_contact"),
            pickup_address=str(data["pickup_address"]),
            food_items=[FoodItem.from_dict(item) for item in data["food_items"]],
            prepared_at=parse_datetime(data.get("prepared_at")),
            available_until=require_datetime(data["available_until"]),
            storage=str(data["storage"]),
            notes=str(data.get("notes", "")),
        )


@dataclass(frozen=True)
class Recipient:
    recipient_id: str
    name: str
    recipient_type: str
    address: str
    accepts_categories: set[str]
    capacity_meals: int
    hours: dict[str, str]
    contact_method: str
    contact_value: str
    pickup_supported: bool
    distance_miles_demo: float
    handling_notes: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Recipient":
        return cls(
            recipient_id=str(data["recipient_id"]),
            name=str(data["name"]),
            recipient_type=str(data["recipient_type"]),
            address=str(data["address"]),
            accepts_categories={str(item) for item in data["accepts_categories"]},
            capacity_meals=int(data["capacity_meals"]),
            hours=dict(data["hours"]),
            contact_method=str(data["contact_method"]),
            contact_value=str(data["contact_value"]),
            pickup_supported=bool(data["pickup_supported"]),
            distance_miles_demo=float(data["distance_miles_demo"]),
            handling_notes=str(data["handling_notes"]),
        )


@dataclass(frozen=True)
class SafetyDecision:
    status: SafetyStatus
    reasons: list[str]
    prompt_injection_signals: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MatchCandidate:
    recipient: Recipient
    score: float
    reasons: list[str]


@dataclass
class WorkflowResult:
    final_state: DonationState
    safety_status: SafetyStatus | None = None
    reasons: list[str] = field(default_factory=list)
    prompt_injection_signals: list[str] = field(default_factory=list)
    selected_recipient_id: str | None = None
    ranked_candidates: list[MatchCandidate] = field(default_factory=list)
    draft_message: str | None = None
    approval_id: str | None = None
    tool_calls: list[str] = field(default_factory=list)
    trace_events: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)


def parse_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    return require_datetime(value)


def require_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        raise TypeError(f"Expected datetime string, got {type(value).__name__}")
    return datetime.fromisoformat(value)

