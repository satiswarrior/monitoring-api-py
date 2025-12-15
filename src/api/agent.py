from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.security.agent_key import verify_agent_key
from src.models.agent_models import AgentStatusRequest, AgentAlertsRequest, CommandResultRequest
from src.models.db_models import ResultStatus, CommandStatus
from src.database import get_session
from src.models.db_models import Server, Alert, CommandQueue, CommandResult

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/status")
async def post_status(req: AgentStatusRequest, session: AsyncSession = Depends(get_session),
                      key: str = Depends(verify_agent_key)):
    """Обновить/вставить статус сервера, отправленный агентом.
    - Если сервер с `req.server_id` существует, обновить поля и last_update/last_status.
    - В противном случае создать новую запись `Server`.
    """
    stmt = select(Server).where(Server.id == req.server_id)
    result = await session.execute(stmt)
    server = result.scalars().first()

    if server is None:
        raise HTTPException(status_code=404, detail="Invalid server ID")

    async with session.begin():
        server.region_id = req.region_id
        server.ip = req.ip
        server.cgm_version = req.cgm_version
        server.admin_version = req.admin_version
        server.last_update = req.timestamp

        if hasattr(req, 'raw_status'):
            server.last_status = req.raw_status

    return {"message": "Status stored", "server_id": req.server_id}


@router.post("/alerts")
async def post_alerts(req: AgentAlertsRequest, session: AsyncSession = Depends(get_session),
                      key: str = Depends(verify_agent_key)):
    """Вставка alerts для сервера.

    Простое поведение: вставка каждой строки alert. Логику дедупликации/агрегации можно добавить позже."""
    if not req.alerts:
        return {"message": "No alerts", "count": 0}

    inserted = 0
    async with session.begin():
        for a in req.alerts:
            alert = Alert(
                server_id=req.server_id,
                severity=a.severity,
                source=a.source,
                alert_text=a.alert,
                counter=a.counter or 1,
                stacktrace=getattr(a, "stackTrace", None),
                timestamp=a.timestamp,
                active=True,
            )
            session.add(alert)
            inserted += 1

    return {"message": "Alerts stored", "count": inserted}


@router.get("/commands")
async def get_commands(server_id: int, session: AsyncSession = Depends(get_session), key: str = Depends(verify_agent_key)):
    """Возвращает pending команды для сервера.

    Ответ представляет собой список словарей: {id, type, payload}
    """
    stmt = (select(CommandQueue)
            .where(CommandQueue.server_id == server_id, CommandQueue.status == CommandStatus.pending))
    result = await session.execute(stmt)
    rows = result.scalars().all()
    return {"data": [{"id": r.id, "type": r.type, "payload": r.payload} for r in rows]}


@router.post("/commands/{command_id}/result")
async def command_result(command_id: int, req: CommandResultRequest, session: AsyncSession = Depends(get_session),
                         key: str = Depends(verify_agent_key)):
    async with session.begin():
        stmt = select(CommandQueue).where(CommandQueue.id == command_id)
        res = await session.execute(stmt)
        cmd = res.scalars().first()
        if cmd is None:
            raise HTTPException(status_code=404, detail="command not found")

        # insert result
        result_row = CommandResult(command_id=cmd.id, status=req.status, message=req.message)
        session.add(result_row)
        # flush so DB defaults (created_at) are available, then refresh
        await session.flush()
        try:
            await session.refresh(result_row)
        except Exception:
            pass

        # update command status
        if req.status in {status.value for status in ResultStatus}:
            cmd.status = req.status
            if req.status == ResultStatus.done:
                cmd.executed_at = getattr(result_row, 'created_at', None)


    return {"message": "Result saved", "command_id": command_id}
