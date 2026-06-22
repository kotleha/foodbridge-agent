from foodbridge_agent.tools import (
    request_dispatch_approval_tool,
    schedule_approved_dispatch_tool,
    search_recipients_tool,
    triage_food_safety_tool,
)


def test_triage_tool_returns_structured_success():
    result = triage_food_safety_tool(
        donor_name="Bluebird Cafe",
        donor_contact="ops@bluebird.example.test",
        pickup_address="120 Market St",
        food_items=[
            {
                "name": "sealed veggie wraps",
                "quantity": 24,
                "category": "prepared_meal",
                "sealed": True,
            }
        ],
        prepared_at="2026-06-22T15:00:00",
        available_until="2026-06-22T21:00:00",
        storage="refrigerated",
        notes="Kept cold.",
    )

    assert result["status"] == "success"
    assert result["safety_status"] == "eligible"
    assert result["next_valid_actions"] == ["search_recipients"]


def test_search_recipients_tool_uses_local_directory_adapter():
    result = search_recipients_tool(["prepared_meal"], 30)

    assert result["status"] == "success"
    assert result["items"]
    assert all(item["capacity_meals"] >= 30 for item in result["items"])


def test_approval_tool_is_pending_by_default():
    result = request_dispatch_approval_tool("dsp_test", "rcp_harbor_house", "Preview")

    assert result["status"] == "approval_pending"
    assert result["approval_id"] == "apr_dsp_test"
    assert result["scope"] == "single_dispatch_only"


def test_schedule_tool_requires_approved_status():
    denied = schedule_approved_dispatch_tool("dsp_test", "apr_test", "pending")
    approved = schedule_approved_dispatch_tool("dsp_test", "apr_test", "approved")

    assert denied["status"] == "error"
    assert denied["type"] == "permission_denied"
    assert approved["status"] == "success"
    assert approved["dispatch_state"] == "scheduled"

