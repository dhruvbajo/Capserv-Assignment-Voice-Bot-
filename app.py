from fastapi import FastAPI, HTTPException
from models import BotRequest, BotResponse
from nlu import parse_transcript
import crm_client
from logger import logger

# ---------- FastAPI App ----------
app = FastAPI(title="Voice Bot Service")  # Initialize FastAPI app

# ---------- Bot Endpoint ----------
@app.post("/bot/handle", response_model=BotResponse)
def handle_bot(req: BotRequest):
    transcript = req.transcript  # Get transcript from request

    # ---------- Validation ----------
    if len(transcript) > 1000:  # Reject overly long transcripts
        return BotResponse(
            intent="UNKNOWN",
            error={"type":"VALIDATION_ERROR","details":"Transcript too long"}
        )

    # ---------- Parse Transcript ----------
    intent, entities = parse_transcript(transcript)  # Extract intent & entities via NLU
    
    logger.info(f"Transcript: {transcript}, Intent: {intent}, Entities: {entities}")  # Log parsing info

    # ---------- Handle LEAD_CREATE ----------
    if intent == "LEAD_CREATE":
        if not all(k in entities for k in ["name","phone","city"]):  # Validate required fields
            return BotResponse(
                intent=intent,
                error={"type":"VALIDATION_ERROR","details":"Missing required fields"}
            )
        # Call CRM to create lead
        crm_resp = crm_client.create_lead(
            entities["name"], entities["phone"], entities["city"], entities.get("source")
        )
        return BotResponse(
            intent=intent,
            entities=entities,
            crm_call={"endpoint":"/crm/leads","method":"POST","status_code":200},  # Log CRM call info
            result={"message":crm_resp}  # Return CRM response
        )

    # ---------- Handle VISIT_SCHEDULE ----------
    elif intent == "VISIT_SCHEDULE":
        if not all(k in entities for k in ["lead_id","visit_time"]):  # Validate required fields
            return BotResponse(
                intent=intent,
                error={"type":"VALIDATION_ERROR","details":"Missing required fields"}
            )
        # Call CRM to schedule visit
        crm_resp = crm_client.schedule_visit(
            entities["lead_id"], entities["visit_time"], entities.get("notes")
        )
        return BotResponse(
            intent=intent,
            entities=entities,
            crm_call={"endpoint":"/crm/visits","method":"POST","status_code":200},
            result={"message":crm_resp}
        )

    # ---------- Handle LEAD_UPDATE ----------
    elif intent == "LEAD_UPDATE":
        if not all(k in entities for k in ["lead_id","status"]):  # Validate required fields
            return BotResponse(
                intent=intent,
                error={"type":"VALIDATION_ERROR","details":"Missing required fields"}
            )
        # Call CRM to update lead status
        crm_resp = crm_client.update_lead_status(
            entities["lead_id"], entities["status"], entities.get("notes")
        )
        return BotResponse(
            intent=intent,
            entities=entities,
            crm_call={
                "endpoint": f"/crm/leads/{entities['lead_id']}/status",
                "method":"POST",
                "status_code":200
            },
            result={"message":crm_resp}
        )

    # ---------- Unknown Intent ----------
    else:
        return BotResponse(
            intent="UNKNOWN",
            error={"type":"PARSING_ERROR","details":"Could not determine intent"}  # Handle unrecognized transcripts
        )
