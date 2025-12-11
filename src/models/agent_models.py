from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AgentStatusRequest(BaseModel):
    agent_key: str
    server_id: int
    ip: str
    cgm_version: str
    admin_version: str
    timestamp: datetime


class AlertItem(BaseModel):
    severity: str
    source: str
    alert: str
    counter: int
    stackTrace: Optional[str] = None


class AgentAlertsRequest(BaseModel):
    agent_key: str
    server_id: int
    alerts: List[AlertItem]


class Command(BaseModel):
    command_id: int
    type: str
    payload: dict | None = None


class CommandResultRequest(BaseModel):
    status: str
    message: Optional[str] = None
