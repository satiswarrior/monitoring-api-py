from pydantic import BaseModel
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Server(BaseModel):
    id: int
    region_id: int
    region_name: str
    ip: str
    cgm_version: str
    admin_version: str
    last_update: datetime
    has_critical_alerts: bool
