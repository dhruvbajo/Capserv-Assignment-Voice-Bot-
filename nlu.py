import re
import json
import dateparser
from typing import Dict
from logger import logger
from settings import LLM_API_KEY
import openai

# ---------- OpenAI Setup ----------
if LLM_API_KEY:
    openai.api_key = LLM_API_KEY

# ---------- Rule-based Intent Keywords ----------
INTENT_KEYWORDS = {
    "LEAD_CREATE": ["add a new lead", "create lead", "new lead","add a lead","add lead"],
    "VISIT_SCHEDULE": ["schedule a visit", "fix a visit", "book a visit","schedule visit"],
    "LEAD_UPDATE": ["update lead", "mark lead", "change status"],
}

PHONE_REGEX = r"\b\d{10}\b"
UUID_REGEX = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

# ---------- Rule-based Extraction ----------
def extract_intent_rule(transcript: str) -> str:
    transcript_lower = transcript.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(k in transcript_lower for k in keywords):
            return intent
    return "UNKNOWN"

def extract_entities_rule(transcript: str, intent: str) -> Dict:
    entities = {}
    if intent == "LEAD_CREATE":
        # Name extraction
        name_match = re.search(r"lead ([\w\s]+?) email", transcript, re.I)
        if name_match:
            entities["name"] = name_match.group(1).strip()

        # Email
        email_match = re.search(r"email ([\w\.-]+@[\w\.-]+)", transcript, re.I)
        if email_match:
            entities["email"] = email_match.group(1).strip()

        # Phone
        phone_match = re.search(r"\b\d{10}\b", transcript)
        if phone_match:
            entities["phone"] = phone_match.group(0).strip()

        # City
        city_match = re.search(r"from ([\w\s]+?) (source|$)", transcript, re.I)
        if city_match:
            entities["city"] = city_match.group(1).strip()

        # Source
        source_match = re.search(r"source ([\w\s]+)", transcript, re.I)
        if source_match:
            entities["source"] = source_match.group(1).strip()

    elif intent == "VISIT_SCHEDULE":
        lead_match = re.search(UUID_REGEX, transcript)
        if lead_match:
            entities["lead_id"] = lead_match.group(0)

        # Try ISO 8601 first
        iso_match = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2})?", transcript)
        if iso_match:
            entities["visit_time"] = iso_match.group(0)
        else:
            # fallback to human-readable parsing
            date_text_match = re.search(r"on (.+?) (with|$)", transcript, re.I)
            if date_text_match:
                date_text = date_text_match.group(1).strip()
                date_match = dateparser.parse(date_text, settings={'PREFER_DATES_FROM': 'future'})
                if date_match:
                    entities["visit_time"] = date_match.isoformat()





    elif intent == "LEAD_UPDATE":
        lead_match = re.search(UUID_REGEX, transcript)
        if lead_match:
            entities["lead_id"] = lead_match.group(0)
        status_match = re.search(r"(NEW|IN_PROGRESS|FOLLOW_UP|WON|LOST)", transcript, re.I)
        if status_match:
            entities["status"] = status_match.group(1).upper()

    return entities

# ---------- LLM Extraction ----------
def extract_intent_llm(transcript: str) -> str:
    prompt = f"""
    You are a CRM assistant. Classify the following text into one of these intents:
    LEAD_CREATE, VISIT_SCHEDULE, LEAD_UPDATE, UNKNOWN.
    Text: "{transcript}"
    """
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        intent_text = resp.choices[0].message.content.strip().upper()
        for intent in ["LEAD_CREATE", "VISIT_SCHEDULE", "LEAD_UPDATE", "UNKNOWN"]:
            if intent in intent_text:
                return intent
        return "UNKNOWN"
    except Exception as e:
        logger.error(f"LLM intent extraction failed: {e}")
        return "UNKNOWN"

def extract_entities_llm(transcript: str) -> dict:
    prompt = f"""
    You are a CRM assistant. Extract entities from this transcript.
    Return JSON with keys:
    - LEAD_CREATE: name, phone, city, source
    - VISIT_SCHEDULE: lead_id, visit_time, notes
    - LEAD_UPDATE: lead_id, status, notes
    Text: "{transcript}"
    """
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        text = resp.choices[0].message.content.strip()
        entities = json.loads(text)
        return entities
    except Exception as e:
        logger.error(f"LLM entity extraction failed: {e}")
        return {}


def parse_transcript(transcript: str) -> (str, Dict):
    intent = extract_intent_rule(transcript)
    entities = extract_entities_rule(transcript, intent)
    
    logger.info(f"Transcript: {transcript}")
    logger.info(f"Rule-based intent: {intent}, entities: {entities}")

    # fallback to LLM only if intent unknown OR entities empty
    if intent == "UNKNOWN" or (intent != "UNKNOWN" and not entities):
        logger.info("Falling back to OpenAI LLM for NLU")
        llm_intent = extract_intent_llm(transcript)
        llm_entities = extract_entities_llm(transcript)

        if llm_intent != "UNKNOWN" and llm_entities:
            intent = llm_intent
            entities = llm_entities

    return intent, entities
