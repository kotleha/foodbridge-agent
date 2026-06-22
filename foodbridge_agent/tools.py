"""Structured tool wrappers for the FoodBridge agent layer."""

from __future__ import annotations

from typing import Any

from foodbridge_agent.models import Donation, SafetyStatus
from foodbridge_agent.recipients import rank_recipient_matches
from foodbridge_agent.safety import triage_food_safety
from mcp_servers.recipient_directory.server import search_recipients as search_recipient_directory


def triage_food_safety_tool(
    donor_name: str,
    pickup_address: str,
    food_items: list[dict[str, Any]],
    available_until: str,
    storage: str,
    notes: str = "",
    donor_contact: str | None = None,
    prepared_at: str | None = None,
) -> dict[str, Any]:
    """Check whether a donation can proceed to recipient matching."""
    try:
        donation = Donation.from_dict(
            {
                "donor_name": donor_name,
                "donor_contact": donor_contact,
                "pickup_address": pickup_address,
                "food_items": food_items,
                "prepared_at": prepared_at,
                "available_until": available_until,
                "storage": storage,
                "notes": notes,
            }
        )
        decision = triage_food_safety(donation)
        return {
            "status": "success",
            "safety_status": decision.status.value,
            "reasons": decision.reasons,
            "prompt_injection_signals": decision.prompt_injection_signals,
            "next_valid_actions": _next_actions_for_safety(decision.status),
        }
    except Exception as exc:
        return {
            "status": "error",
            "type": type(exc).__name__,
            "message": str(exc),
            "next_valid_actions": ["ask_user_for_valid_donation_fields"],
        }


def search_recipients_tool(
    food_categories: list[str],
    needed_capacity_meals: int,
    max_distance_miles: float = 10.0,
) -> dict[str, Any]:
    """Search the local recipient directory adapter."""
    try:
        items = search_recipient_directory(food_categories, needed_capacity_meals, max_distance_miles)
        return {
            "status": "success",
            "items": items,
            "summary": f"Found {len(items)} eligible recipients.",
            "next_valid_actions": ["rank_recipient_matches"] if items else ["ask_user_to_expand_search"],
        }
    except Exception as exc:
        return {
            "status": "error",
            "type": type(exc).__name__,
            "message": str(exc),
            "next_valid_actions": ["retry_recipient_search", "ask_user_to_review_directory"],
        }


def rank_recipient_matches_tool(donation: dict[str, Any], recipient_ids: list[str] | None = None) -> dict[str, Any]:
    """Rank matching recipients for a donation using deterministic MVP scoring."""
    try:
        from foodbridge_agent.recipients import load_recipients

        parsed = Donation.from_dict(donation)
        recipients = load_recipients()
        if recipient_ids is not None:
            allowed = set(recipient_ids)
            recipients = [recipient for recipient in recipients if recipient.recipient_id in allowed]

        ranked = rank_recipient_matches(parsed, recipients)
        return {
            "status": "success",
            "candidates": [
                {
                    "recipient_id": candidate.recipient.recipient_id,
                    "name": candidate.recipient.name,
                    "score": candidate.score,
                    "reasons": candidate.reasons,
                }
                for candidate in ranked
            ],
            "next_valid_actions": ["draft_dispatch_message"] if ranked else ["ask_user_to_expand_search"],
        }
    except Exception as exc:
        return {
            "status": "error",
            "type": type(exc).__name__,
            "message": str(exc),
            "next_valid_actions": ["ask_user_to_review_donation_fields"],
        }


def draft_dispatch_message_tool(
    donor_name: str,
    pickup_address: str,
    recipient_name: str,
    food_items: list[dict[str, Any]],
    available_until: str,
) -> dict[str, Any]:
    """Draft a recipient message without sending it."""
    try:
        item_summary = ", ".join(f"{int(item['quantity'])} {item['name']}" for item in food_items)
        draft = (
            f"Hello {recipient_name}, {donor_name} has surplus food available: "
            f"{item_summary}. Pickup is available at {pickup_address} until {available_until}. "
            "Please confirm whether you can accept this donation."
        )
        return {
            "status": "success",
            "draft_message": draft,
            "redactions": [],
            "next_valid_actions": ["request_dispatch_approval"],
        }
    except Exception as exc:
        return {
            "status": "error",
            "type": type(exc).__name__,
            "message": str(exc),
            "next_valid_actions": ["ask_user_to_review_message_inputs"],
        }


def request_dispatch_approval_tool(dispatch_id: str, recipient_id: str, draft_message: str) -> dict[str, Any]:
    """Create an approval request for simulated external communication."""
    return {
        "status": "approval_pending",
        "approval_id": f"apr_{dispatch_id}",
        "approval_type": "simulated_external_send",
        "risk": "external_communication",
        "target": recipient_id,
        "preview": draft_message,
        "scope": "single_dispatch_only",
        "next_valid_actions": ["wait_for_human_approval"],
    }


def schedule_approved_dispatch_tool(dispatch_id: str, approval_id: str, approval_status: str) -> dict[str, Any]:
    """Schedule a simulated dispatch only when approval is explicit."""
    if approval_status != "approved":
        return {
            "status": "error",
            "type": "permission_denied",
            "message": "Dispatch scheduling requires approved human approval.",
            "next_valid_actions": ["request_dispatch_approval"],
        }

    return {
        "status": "success",
        "dispatch_id": dispatch_id,
        "approval_id": approval_id,
        "dispatch_state": "scheduled",
        "summary": "Approved simulated dispatch has been scheduled.",
    }


def _next_actions_for_safety(status: SafetyStatus) -> list[str]:
    if status == SafetyStatus.ELIGIBLE:
        return ["search_recipients"]
    if status == SafetyStatus.NEEDS_REVIEW:
        return ["ask_user_for_missing_safety_fields"]
    return ["stop_workflow"]

