import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dashboard_serves_html():
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "FoodBridge Agent" in response.text


def test_demo_endpoint_runs_happy_path():
    client = TestClient(create_app())

    response = client.post("/api/demo/happy_path")

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["final_state"] == "APPROVAL_PENDING"
    assert body["result"]["selected_recipient_id"] == "rcp_harbor_house"


def test_demo_endpoint_rejects_unknown_scenario():
    client = TestClient(create_app())

    response = client.post("/api/demo/not-real")

    assert response.status_code == 404


def test_persisted_demo_scenario_can_resolve_approval(tmp_path, monkeypatch):
    db_path = tmp_path / "foodbridge.sqlite"
    monkeypatch.setenv("FOODBRIDGE_DB_PATH", str(db_path))
    client = TestClient(create_app())

    created = client.post("/api/demo/happy_path?persist=true")
    approval_id = created.json()["result"]["approval_id"]
    resolved = client.post(
        f"/api/approvals/{approval_id}",
        json={"status": "approved", "approved_by": "demo_operator"},
    )

    assert created.status_code == 200
    assert created.json()["persisted"] is True
    assert resolved.status_code == 200
    assert resolved.json()["snapshot"]["donation"]["state"] == "SCHEDULED"


def test_donation_endpoint_runs_custom_payload():
    client = TestClient(create_app())
    payload = {
        "donation_id": "don_api_test",
        "donor_name": "Bluebird Cafe",
        "donor_contact": "ops@bluebird.example.test",
        "pickup_address": "120 Market St",
        "food_items": [
            {
                "name": "sealed veggie wraps",
                "quantity": 24,
                "category": "prepared_meal",
                "sealed": True,
            }
        ],
        "prepared_at": "2026-06-22T15:00:00",
        "available_until": "2026-06-22T21:00:00",
        "storage": "refrigerated",
        "notes": "Kept cold.",
    }

    response = client.post("/api/donations", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["persisted"] is False
    assert body["result"]["final_state"] == "APPROVAL_PENDING"


def test_persisted_donation_can_resolve_approval(tmp_path, monkeypatch):
    db_path = tmp_path / "foodbridge.sqlite"
    monkeypatch.setenv("FOODBRIDGE_DB_PATH", str(db_path))
    client = TestClient(create_app())
    payload = {
        "donation_id": "don_api_persisted",
        "donor_name": "Bluebird Cafe",
        "donor_contact": "ops@bluebird.example.test",
        "pickup_address": "120 Market St",
        "food_items": [
            {
                "name": "sealed veggie wraps",
                "quantity": 24,
                "category": "prepared_meal",
                "sealed": True,
            }
        ],
        "prepared_at": "2026-06-22T15:00:00",
        "available_until": "2026-06-22T21:00:00",
        "storage": "refrigerated",
        "notes": "Kept cold.",
    }

    created = client.post("/api/donations?persist=true", json=payload)
    approval_id = created.json()["result"]["approval_id"]
    resolved = client.post(
        f"/api/approvals/{approval_id}",
        json={"status": "approved", "approved_by": "demo_operator"},
    )

    assert created.status_code == 200
    assert created.json()["persisted"] is True
    assert resolved.status_code == 200
    assert resolved.json()["snapshot"]["donation"]["state"] == "SCHEDULED"


def test_approval_endpoint_rejects_invalid_status():
    client = TestClient(create_app())

    response = client.post("/api/approvals/apr_missing", json={"status": "maybe"})

    assert response.status_code == 400
