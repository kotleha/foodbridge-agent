"""Local recipient directory MCP server for FoodBridge.

The deterministic eval harness reads the same seed data directly. This server is the MCP-facing
adapter that the ADK agent will use in the next implementation layer.
"""

from __future__ import annotations

from typing import Any

from foodbridge_agent.recipients import load_recipients

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover - this keeps the repo usable before MCP deps are installed.
    FastMCP = None


def list_recipients() -> list[dict[str, Any]]:
    recipients = load_recipients()
    return [
        {
            "recipient_id": recipient.recipient_id,
            "name": recipient.name,
            "recipient_type": recipient.recipient_type,
            "accepts_categories": sorted(recipient.accepts_categories),
            "capacity_meals": recipient.capacity_meals,
            "pickup_supported": recipient.pickup_supported,
            "distance_miles_demo": recipient.distance_miles_demo,
        }
        for recipient in recipients
    ]


def search_recipients(
    food_categories: list[str],
    needed_capacity_meals: int,
    max_distance_miles: float = 10.0,
) -> list[dict[str, Any]]:
    categories = set(food_categories)
    matches = []
    for recipient in load_recipients():
        if not categories.issubset(recipient.accepts_categories):
            continue
        if recipient.capacity_meals < needed_capacity_meals:
            continue
        if recipient.distance_miles_demo > max_distance_miles:
            continue
        matches.append(
            {
                "recipient_id": recipient.recipient_id,
                "name": recipient.name,
                "capacity_meals": recipient.capacity_meals,
                "distance_miles_demo": recipient.distance_miles_demo,
                "pickup_supported": recipient.pickup_supported,
                "handling_notes": recipient.handling_notes,
            }
        )
    return matches


def get_recipient(recipient_id: str) -> dict[str, Any] | None:
    for recipient in load_recipients():
        if recipient.recipient_id == recipient_id:
            return {
                "recipient_id": recipient.recipient_id,
                "name": recipient.name,
                "recipient_type": recipient.recipient_type,
                "address": recipient.address,
                "accepts_categories": sorted(recipient.accepts_categories),
                "capacity_meals": recipient.capacity_meals,
                "hours": recipient.hours,
                "contact_method": recipient.contact_method,
                "contact_value": recipient.contact_value,
                "pickup_supported": recipient.pickup_supported,
                "distance_miles_demo": recipient.distance_miles_demo,
                "handling_notes": recipient.handling_notes,
            }
    return None


def build_mcp_server():
    if FastMCP is None:
        raise RuntimeError("Install the `mcp` package to run the recipient directory MCP server.")

    server = FastMCP("foodbridge-recipient-directory")
    server.tool()(list_recipients)
    server.tool()(search_recipients)
    server.tool()(get_recipient)
    return server


def main() -> None:
    build_mcp_server().run()


if __name__ == "__main__":
    main()

