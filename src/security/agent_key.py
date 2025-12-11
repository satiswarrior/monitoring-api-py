from fastapi import Header, HTTPException
from src.config import settings

def verify_agent_key(x_api_key: str = Header(...)):
    if x_api_key not in settings.VALID_AGENT_KEYS:
        raise HTTPException(status_code=401, detail="Invalid agent API key")
    return x_api_key
