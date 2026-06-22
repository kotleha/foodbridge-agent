"""FastAPI demo shell for FoodBridge Agent."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from foodbridge_agent.evals import FIXTURE_DIR, run_fixture
from foodbridge_agent.models import Donation
from foodbridge_agent.recipients import load_recipients
from foodbridge_agent.serialization import workflow_result_to_dict
from foodbridge_agent.storage import FoodBridgeStore
from foodbridge_agent.workflow import run_intake

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
except ImportError as exc:  # pragma: no cover - optional dependency guard.
    raise RuntimeError("Install web dependencies with `python3 -m pip install '.[web]'`.") from exc


STATIC_DIR = Path(__file__).resolve().parent / "static"

SCENARIOS = {
    "happy_path": "safe_donation_happy_path.json",
    "unsafe_food": "unsafe_food_rejection.json",
    "prompt_injection": "prompt_injection_donor_notes.json",
    "missing_info": "missing_information_needs_review.json",
    "capacity_mismatch": "recipient_capacity_mismatch.json",
    "resume_pending": "resume_approval_pending.json",
}


def create_app() -> FastAPI:
    app = FastAPI(title="FoodBridge Agent", version="0.1.0")
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> str:
        return (STATIC_DIR / "index.html").read_text(encoding="utf-8")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "foodbridge-agent"}

    @app.get("/api/scenarios")
    def scenarios() -> dict[str, list[str]]:
        return {"scenarios": sorted(SCENARIOS)}

    @app.get("/api/recipients")
    def recipients() -> dict[str, list[dict[str, Any]]]:
        return {
            "recipients": [
                {
                    "recipient_id": recipient.recipient_id,
                    "name": recipient.name,
                    "recipient_type": recipient.recipient_type,
                    "accepts_categories": sorted(recipient.accepts_categories),
                    "capacity_meals": recipient.capacity_meals,
                    "pickup_supported": recipient.pickup_supported,
                    "distance_miles_demo": recipient.distance_miles_demo,
                }
                for recipient in load_recipients()
            ]
        }

    @app.post("/api/demo/{scenario}")
    def run_demo_scenario(scenario: str, persist: bool = False) -> dict[str, Any]:
        fixture = load_scenario_fixture(scenario)
        result = run_fixture(fixture)
        response: dict[str, Any] = {
            "scenario": scenario,
            "persisted": False,
            "result": workflow_result_to_dict(result),
        }

        if persist and "donation" in fixture:
            donation = Donation.from_dict(fixture["donation"], donation_id=f"don_{fixture['id']}")
            store = get_store()
            dispatch_id = store.save_workflow_result(donation, result)
            response["persisted"] = True
            response["donation_id"] = donation.donation_id
            response["dispatch_id"] = dispatch_id
            response["snapshot"] = store.get_snapshot(donation.donation_id)

        return response

    @app.post("/api/donations")
    def create_donation(payload: dict[str, Any], persist: bool = False) -> dict[str, Any]:
        try:
            donation = Donation.from_dict(payload, donation_id=str(payload.get("donation_id", "don_api_demo")))
            result = run_intake(donation)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        response: dict[str, Any] = {"result": workflow_result_to_dict(result)}
        if persist:
            store = get_store()
            dispatch_id = store.save_workflow_result(donation, result)
            response["persisted"] = True
            response["donation_id"] = donation.donation_id
            response["dispatch_id"] = dispatch_id
            response["snapshot"] = store.get_snapshot(donation.donation_id)
        else:
            response["persisted"] = False
        return response

    @app.post("/api/approvals/{approval_id}")
    def resolve_approval(approval_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        status = str(payload.get("status", ""))
        if status not in {"approved", "denied", "cancelled"}:
            raise HTTPException(status_code=400, detail="status must be approved, denied, or cancelled")

        store = get_store()
        try:
            snapshot = store.resolve_approval(
                approval_id=approval_id,
                status=status,
                approved_by=payload.get("approved_by"),
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        return {"approval_id": approval_id, "snapshot": snapshot}

    return app


def get_store() -> FoodBridgeStore:
    return FoodBridgeStore(os.environ.get("FOODBRIDGE_DB_PATH", "foodbridge.sqlite"))


def load_scenario_fixture(scenario: str) -> dict[str, Any]:
    filename = SCENARIOS.get(scenario)
    if filename is None:
        raise HTTPException(status_code=404, detail=f"Unknown scenario: {scenario}")

    path = Path(FIXTURE_DIR) / filename
    return json.loads(path.read_text(encoding="utf-8"))


app = create_app()
