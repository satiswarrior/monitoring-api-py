from fastapi import APIRouter, Depends
from src.security.agent_key import verify_agent_key
from src.models.agent_models import *
from src.mocks.agent_data import COMMANDS

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/status")
def post_status(req: AgentStatusRequest, key: str = Depends(verify_agent_key)):
    return {"message": "Status stored", "server_id": req.server_id}


@router.post("/alerts")
def post_alerts(req: AgentAlertsRequest, key: str = Depends(verify_agent_key)):
    return {"message": "Alerts stored", "count": len(req.alerts)}


@router.get("/commands")
def get_commands(server_id: int, key: str = Depends(verify_agent_key)):
    return COMMANDS.get(server_id, [])


@router.post("/commands/{command_id}/result")
def command_result(command_id: int, req: CommandResultRequest, key: str = Depends(verify_agent_key)):
    return {"message": "Result saved", "command_id": command_id}
