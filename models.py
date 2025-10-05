from pydantic import BaseModel
from typing import Optional, Dict

class BotRequest(BaseModel):
    transcript: str
    metadata: Optional[Dict] = None

class BotResponse(BaseModel):
    intent: str
    entities: Optional[Dict] = None
    crm_call: Optional[Dict] = None
    result: Optional[Dict] = None
    error: Optional[Dict] = None
