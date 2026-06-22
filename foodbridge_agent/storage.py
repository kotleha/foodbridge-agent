"""SQLite persistence for FoodBridge workflow state and traces."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any

from foodbridge_agent.models import Donation, WorkflowResult


class FoodBridgeStore:
    """Small SQLite store for demo-safe workflow persistence."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS donations (
                    donation_id TEXT PRIMARY KEY,
                    donor_name TEXT NOT NULL,
                    state TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS dispatches (
                    dispatch_id TEXT PRIMARY KEY,
                    donation_id TEXT NOT NULL,
                    recipient_id TEXT,
                    state TEXT NOT NULL,
                    draft_message TEXT,
                    approval_id TEXT,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (donation_id) REFERENCES donations(donation_id)
                );

                CREATE TABLE IF NOT EXISTS approvals (
                    approval_id TEXT PRIMARY KEY,
                    dispatch_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    approval_type TEXT NOT NULL,
                    approved_by TEXT,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (dispatch_id) REFERENCES dispatches(dispatch_id)
                );

                CREATE TABLE IF NOT EXISTS trace_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    donation_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def save_workflow_result(self, donation: Donation, result: WorkflowResult) -> str | None:
        """Persist a workflow result and return the dispatch id when one exists."""
        self.initialize()
        dispatch_id = f"dsp_{donation.donation_id}" if result.selected_recipient_id or result.draft_message else None

        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO donations (donation_id, donor_name, state, payload_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(donation_id) DO UPDATE SET
                    donor_name = excluded.donor_name,
                    state = excluded.state,
                    payload_json = excluded.payload_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    donation.donation_id,
                    donation.donor_name,
                    result.final_state.value,
                    json.dumps(donation_to_payload(donation), sort_keys=True),
                ),
            )

            if dispatch_id is not None:
                conn.execute(
                    """
                    INSERT INTO dispatches (dispatch_id, donation_id, recipient_id, state, draft_message, approval_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(dispatch_id) DO UPDATE SET
                        recipient_id = excluded.recipient_id,
                        state = excluded.state,
                        draft_message = excluded.draft_message,
                        approval_id = excluded.approval_id,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        dispatch_id,
                        donation.donation_id,
                        result.selected_recipient_id,
                        result.final_state.value,
                        result.draft_message,
                        result.approval_id,
                    ),
                )

            if result.approval_id and dispatch_id is not None:
                conn.execute(
                    """
                INSERT INTO approvals (approval_id, dispatch_id, status, approval_type, approved_by, payload_json)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(approval_id) DO UPDATE SET
                    dispatch_id = excluded.dispatch_id,
                    status = excluded.status,
                    approval_type = excluded.approval_type,
                    approved_by = excluded.approved_by,
                        payload_json = excluded.payload_json,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        result.approval_id,
                        dispatch_id,
                        "pending",
                        "simulated_external_send",
                        None,
                        json.dumps({"preview": result.draft_message}, sort_keys=True),
                    ),
                )

            for event in result.trace_events:
                conn.execute(
                    """
                    INSERT INTO trace_events (donation_id, event_type, summary)
                    VALUES (?, ?, ?)
                    """,
                    (donation.donation_id, normalize_event_type(event), event),
                )

        return dispatch_id

    def record_approval(self, approval_id: str, status: str, approved_by: str | None = None) -> None:
        self.initialize()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT dispatch_id, payload_json FROM approvals WHERE approval_id = ?",
                (approval_id,),
            ).fetchone()
            if row is None:
                raise KeyError(f"Unknown approval id: {approval_id}")

            payload = json.loads(row["payload_json"])
            payload["resolved_status"] = status
            payload["approved_by"] = approved_by

            conn.execute(
                """
                UPDATE approvals
                SET status = ?, approved_by = ?, payload_json = ?, updated_at = CURRENT_TIMESTAMP
                WHERE approval_id = ?
                """,
                (status, approved_by, json.dumps(payload, sort_keys=True), approval_id),
            )

    def resolve_approval(self, approval_id: str, status: str, approved_by: str | None = None) -> dict[str, Any]:
        """Resolve an approval and update persisted workflow state."""
        self.initialize()
        with self.connect() as conn:
            approval = conn.execute(
                "SELECT * FROM approvals WHERE approval_id = ?",
                (approval_id,),
            ).fetchone()
            if approval is None:
                raise KeyError(f"Unknown approval id: {approval_id}")

            dispatch = conn.execute(
                "SELECT * FROM dispatches WHERE dispatch_id = ?",
                (approval["dispatch_id"],),
            ).fetchone()
            if dispatch is None:
                raise KeyError(f"Unknown dispatch id: {approval['dispatch_id']}")

            payload = json.loads(approval["payload_json"])
            payload["resolved_status"] = status
            payload["approved_by"] = approved_by

            conn.execute(
                """
                UPDATE approvals
                SET status = ?, approved_by = ?, payload_json = ?, updated_at = CURRENT_TIMESTAMP
                WHERE approval_id = ?
                """,
                (status, approved_by, json.dumps(payload, sort_keys=True), approval_id),
            )

            if status == "approved":
                next_state = "SCHEDULED"
                events = ["approval_resolved", "dispatch_scheduled"]
            else:
                next_state = "CANCELLED"
                events = ["approval_resolved", "dispatch_cancelled"]

            conn.execute(
                """
                UPDATE dispatches
                SET state = ?, updated_at = CURRENT_TIMESTAMP
                WHERE dispatch_id = ?
                """,
                (next_state, approval["dispatch_id"]),
            )
            conn.execute(
                """
                UPDATE donations
                SET state = ?, updated_at = CURRENT_TIMESTAMP
                WHERE donation_id = ?
                """,
                (next_state, dispatch["donation_id"]),
            )
            for event in events:
                conn.execute(
                    """
                    INSERT INTO trace_events (donation_id, event_type, summary)
                    VALUES (?, ?, ?)
                    """,
                    (dispatch["donation_id"], event, event),
                )

            donation_id = dispatch["donation_id"]

        return self.get_snapshot(donation_id)

    def get_snapshot(self, donation_id: str) -> dict[str, Any]:
        self.initialize()
        with self.connect() as conn:
            donation = conn.execute(
                "SELECT * FROM donations WHERE donation_id = ?",
                (donation_id,),
            ).fetchone()
            if donation is None:
                raise KeyError(f"Unknown donation id: {donation_id}")

            dispatch = conn.execute(
                "SELECT * FROM dispatches WHERE donation_id = ?",
                (donation_id,),
            ).fetchone()
            approvals = conn.execute(
                """
                SELECT approvals.*
                FROM approvals
                JOIN dispatches ON approvals.dispatch_id = dispatches.dispatch_id
                WHERE dispatches.donation_id = ?
                ORDER BY approvals.updated_at
                """,
                (donation_id,),
            ).fetchall()
            traces = conn.execute(
                "SELECT event_type, summary, created_at FROM trace_events WHERE donation_id = ? ORDER BY id",
                (donation_id,),
            ).fetchall()

        return {
            "donation": row_to_dict(donation),
            "dispatch": row_to_dict(dispatch) if dispatch is not None else None,
            "approvals": [row_to_dict(row) for row in approvals],
            "trace_events": [row_to_dict(row) for row in traces],
        }

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn


def donation_to_payload(donation: Donation) -> dict[str, Any]:
    payload = asdict(donation)
    payload["prepared_at"] = donation.prepared_at.isoformat() if donation.prepared_at else None
    payload["available_until"] = donation.available_until.isoformat()
    return payload


def normalize_event_type(event: str) -> str:
    if event.startswith("state:"):
        return "state_transition"
    return event


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}
