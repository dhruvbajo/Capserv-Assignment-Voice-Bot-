import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys, os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app

# Create FastAPI test client
client = TestClient(app)


# ---------------- Test: Successful Visit Scheduling ----------------
@patch("app.parse_transcript")              # Mock intent parser
@patch("app.crm_client.schedule_visit")     # Mock CRM API call
def test_visit_schedule_success(mock_schedule_visit, mock_parse):
    # Mock NLU output
    mock_parse.return_value = (
        "VISIT_SCHEDULE",
        {
            "lead_id": "123e4567-e89b-12d3-a456-426614174000",
            "visit_time": "2025-10-10T16:00:00",
            "notes": "Discuss requirements"
        }
    )

    # Mock CRM response
    mock_schedule_visit.return_value = {
        "visit_id": "f8eea39c-6c97-4a99-a0eb-8dde0db4811b",
        "status": "SCHEDULED"
    }

    # Input transcript
    transcript = "Schedule a visit for lead 123e4567-e89b-12d3-a456-426614174000 on 10th Oct 2025 at 4 PM with notes 'Discuss requirements'."

    # Send request
    response = client.post("/bot/handle", json={"transcript": transcript})
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert data["intent"] == "VISIT_SCHEDULE"
    assert "lead_id" in data["entities"]
    assert "visit_time" in data["entities"]
    assert data["crm_call"]["status_code"] == 200
    assert data["result"]["message"]["status"] == "SCHEDULED"


# ---------------- Test: Missing Required Fields ----------------
@patch("app.parse_transcript")  # Mock intent parser
def test_visit_schedule_missing_fields(mock_parse):
    # Mock missing entities
    mock_parse.return_value = ("VISIT_SCHEDULE", {})

    # Incomplete transcript
    transcript = "Schedule a visit"

    # Send request
    response = client.post("/bot/handle", json={"transcript": transcript})
    data = response.json()

    # Assertions
    assert data["error"] is not None
    assert data["error"]["type"] == "VALIDATION_ERROR"
