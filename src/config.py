import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_VERSION = "/api/v1"

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
    JWT_ALGORITHM = "HS256"

    # Agent API keys (пока просто список)
    VALID_AGENT_KEYS = {
        "agent-key-1",
        "agent-key-2"
    }

settings = Settings()
