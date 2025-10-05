import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys, os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app

# Create FastAPI test client
client = TestClient(app)


# ---------------- Test: Successful Lead Creation ----------------
@patch("app.parse_transcript")             # Mock intent parser
@patch("app.crm_client.create_lead")       # Mock CRM API call
def test_lead_create_success(mock_create_lead, mock_parse):
    # Mock NLU output
    mock_parse.return_value = (
        "LEAD_CREATE",
        {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "9876543210",
            "source": "Instagram",
            "city": "Mumbai"
        }
    )

    # Mock CRM response
    mock_create_lead.return_value = {"lead_id": "1234-uuid", "status": "success"}

    # Input transcript
    transcript = "Create lead John Doe email john@example.com phone 9876543210 from Instagram city Mumbai."

    # Send request to API
    response = client.post("/bot/handle", json={"transcript": transcript})
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert data["intent"] == "LEAD_CREATE"
    assert data["entities"] is not None
    assert "email" in data["entities"]
    assert "name" in data["entities"]
    assert "phone" in data["entities"]
    assert "source" in data["entities"]
    assert data["crm_call"]["status_code"] == 200
    assert "lead_id" in data["result"]["message"]


# ---------------- Test: Missing Required Fields ----------------
@patch("app.parse_transcript")  # Mock intent parser
def test_lead_create_missing_fields(mock_parse):
    # Mock missing entities
    mock_parse.return_value = ("LEAD_CREATE", {})

    # Incomplete transcript
    transcript = "Create a new lead"

    # Send request
    response = client.post("/bot/handle", json={"transcript": transcript})
    data = response.json()

    # Assertions
    assert response.status_code in [200, 400]
    assert data["error"] is not None
    assert data["error"]["type"] in ["VALIDATION_ERROR", "PARSING_ERROR"]
