import os
from dotenv import load_dotenv

load_dotenv()

CRM_BASE_URL = os.getenv("CRM_BASE_URL", "http://localhost:8001")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LLM_API_KEY = os.getenv("LLM_API_KEY", None)  # if using Gemini or OpenAI
