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
    
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")  
    db_user = os.getenv("DB_USER", "user")
    db_pass = os.getenv("DB_PASS", "password")
    db_name = os.getenv("DB_NAME", "monitoring")

    DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

settings = Settings()
