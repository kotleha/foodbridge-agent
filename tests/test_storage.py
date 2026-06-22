import json
from pathlib import Path

import pytest

from foodbridge_agent.evals import load_json
from foodbridge_agent.models import Donation
from foodbridge_agent.storage import FoodBridgeStore
from foodbridge_agent.workflow import run_intake

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "evals" / "fixtures"


def test_store_persists_happy_path_snapshot(tmp_path):
    fixture = load_json(FIXTURE_DIR / "safe_donation_happy_path.json")
    donation = Donation.from_dict(fixture["donation"], donation_id="don_storage_happy_path")
    result = run_intake(donation)
    store = FoodBridgeStore(tmp_path / "foodbridge.sqlite")

    dispatch_id = store.save_workflow_result(donation, result)
    snapshot = store.get_snapshot(donation.donation_id)

    assert dispatch_id == "dsp_don_storage_happy_path"
    assert snapshot["donation"]["state"] == "APPROVAL_PENDING"
    assert snapshot["dispatch"]["recipient_id"] == "rcp_harbor_house"
    assert snapshot["dispatch"]["approval_id"] == result.approval_id
    assert snapshot["approvals"][0]["status"] == "pending"
    assert len(snapshot["trace_events"]) >= 5


def test_store_records_approval_resolution(tmp_path):
    fixture = load_json(FIXTURE_DIR / "safe_donation_happy_path.json")
    donation = Donation.from_dict(fixture["donation"], donation_id="don_storage_approval")
    result = run_intake(donation)
    store = FoodBridgeStore(tmp_path / "foodbridge.sqlite")
    store.save_workflow_result(donation, result)

    assert result.approval_id is not None
    store.record_approval(result.approval_id, "approved", approved_by="demo_operator")
    snapshot = store.get_snapshot(donation.donation_id)

    approval = snapshot["approvals"][0]
    payload = json.loads(approval["payload_json"])
    assert approval["status"] == "approved"
    assert approval["approved_by"] == "demo_operator"
    assert payload["resolved_status"] == "approved"


def test_store_resolve_approval_updates_workflow_state(tmp_path):
    fixture = load_json(FIXTURE_DIR / "safe_donation_happy_path.json")
    donation = Donation.from_dict(fixture["donation"], donation_id="don_storage_resolve")
    result = run_intake(donation)
    store = FoodBridgeStore(tmp_path / "foodbridge.sqlite")
    store.save_workflow_result(donation, result)

    assert result.approval_id is not None
    snapshot = store.resolve_approval(result.approval_id, "approved", approved_by="demo_operator")

    assert snapshot["donation"]["state"] == "SCHEDULED"
    assert snapshot["dispatch"]["state"] == "SCHEDULED"
    assert snapshot["approvals"][0]["status"] == "approved"
    assert any(event["event_type"] == "dispatch_scheduled" for event in snapshot["trace_events"])


def test_store_denied_approval_cancels_workflow(tmp_path):
    fixture = load_json(FIXTURE_DIR / "safe_donation_happy_path.json")
    donation = Donation.from_dict(fixture["donation"], donation_id="don_storage_denied")
    result = run_intake(donation)
    store = FoodBridgeStore(tmp_path / "foodbridge.sqlite")
    store.save_workflow_result(donation, result)

    assert result.approval_id is not None
    snapshot = store.resolve_approval(result.approval_id, "denied", approved_by="demo_operator")

    assert snapshot["donation"]["state"] == "CANCELLED"
    assert snapshot["dispatch"]["state"] == "CANCELLED"
    assert any(event["event_type"] == "dispatch_cancelled" for event in snapshot["trace_events"])


def test_store_raises_for_unknown_ids(tmp_path):
    store = FoodBridgeStore(tmp_path / "foodbridge.sqlite")

    with pytest.raises(KeyError):
        store.get_snapshot("missing")

    with pytest.raises(KeyError):
        store.record_approval("missing", "approved")

    with pytest.raises(KeyError):
        store.resolve_approval("missing", "approved")
