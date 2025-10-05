import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys, os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app

# Create FastAPI test client
client = TestClient(app)


# ---------------- Test: Successful Lead Update ----------------
@patch("app.parse_transcript")                 # Mock intent parser
@patch("app.crm_client.update_lead_status")    # Mock CRM API call
def test_lead_update_success(mock_update_lead, mock_parse):
    # Mock NLU output
    mock_parse.return_value = (
        "LEAD_UPDATE",
        {
            "lead_id": "7b1b8f54-aaaa-bbbb-cccc-1234567890ab",
            "status": "WON",
            "notes": "booked unit A2"
        }
    )

    # Mock CRM response
    mock_update_lead.return_value = {"status": "UPDATED"}

    # Input transcript
    transcript = "Update lead 7b1b8f54-aaaa-bbbb-cccc-1234567890ab to WON notes booked unit A2"

    # Send request
    response = client.post("/bot/handle", json={"transcript": transcript})
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert data["intent"] == "LEAD_UPDATE"
    assert data["entities"] is not None
    assert "lead_id" in data["entities"]
    assert "status" in data["entities"]
    assert data["crm_call"]["status_code"] == 200
    assert data["result"]["message"]["status"] == "UPDATED"


# ---------------- Test: Missing Required Fields ----------------
@patch("app.parse_transcript")  # Mock intent parser
def test_lead_update_missing_fields(mock_parse):
    # Mock missing entities
    mock_parse.return_value = ("LEAD_UPDATE", {})

    # Incomplete transcript
    transcript = "Update the lead"

    # Send request
    response = client.post("/bot/handle", json={"transcript": transcript})
    data = response.json()

    # Assertions
    assert data["error"] is not None
    assert data["error"]["type"] == "VALIDATION_ERROR"
