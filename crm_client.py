import requests
from settings import CRM_BASE_URL
from logger import logger

TIMEOUT = 5  # Timeout for CRM API calls in seconds

# ---------- Create Lead ----------
def create_lead(name, phone, city, source=None):
    url = f"{CRM_BASE_URL}/crm/leads"  # CRM endpoint for lead creation
    payload = {"name": name, "phone": phone, "city": city, "source": source}  # Request payload
    try:
        resp = requests.post(url, json=payload, timeout=TIMEOUT)  # POST request to CRM
        resp.raise_for_status()  # Raise exception for HTTP errors
        return resp.json()  # Return JSON response
    except requests.RequestException as e:
        logger.error(f"CRM Error: {e}")  # Log CRM errors
        return {"error": str(e)}  # Return error info

# ---------- Schedule Visit ----------
def schedule_visit(lead_id, visit_time, notes=None):
    url = f"{CRM_BASE_URL}/crm/visits"  # CRM endpoint for scheduling visits
    payload = {"lead_id": lead_id, "visit_time": visit_time, "notes": notes}  # Request payload
    try:
        resp = requests.post(url, json=payload, timeout=TIMEOUT)  # POST request to CRM
        resp.raise_for_status()  # Raise exception for HTTP errors
        return resp.json()  # Return JSON response
    except requests.RequestException as e:
        logger.error(f"CRM Error: {e}")  # Log CRM errors
        return {"error": str(e)}  # Return error info

# ---------- Update Lead Status ----------
def update_lead_status(lead_id, status, notes=None):
    url = f"{CRM_BASE_URL}/crm/leads/{lead_id}/status"  # CRM endpoint for updating lead status
    payload = {"status": status, "notes": notes}  # Request payload
    try:
        resp = requests.post(url, json=payload, timeout=TIMEOUT)  # POST request to CRM
        resp.raise_for_status()  # Raise exception for HTTP errors
        return resp.json()  # Return JSON response
    except requests.RequestException as e:
        logger.error(f"CRM Error: {e}")  # Log CRM errors
        return {"error": str(e)}  # Return error info
