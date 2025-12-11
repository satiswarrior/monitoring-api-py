from fastapi import APIRouter, HTTPException, Depends
from src.models.admin_models import *
from src.security.admin_jwt import create_jwt
from src.mocks.admin_data import SERVERS

router = APIRouter(prefix="/admin", tags=["Admin"])


def auth_admin():
    # Моковая проверка
    return True


@router.post("/auth/login", response_model=LoginResponse)
def login(req: LoginRequest):
    if req.username != "admin" or req.password != "password":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt(req.username)
    return LoginResponse(access_token=token)


@router.get("/servers", response_model=list[Server])
def get_servers(authorized: bool = Depends(auth_admin)):
    return SERVERS


@router.get("/alerts")
def get_alerts(server_id: int, authorized: bool = Depends(auth_admin)):
    return {"server_id": server_id, "alerts": []}


@router.delete("/alerts/{filename}")
def delete_alert(filename: str, authorized: bool = Depends(auth_admin)):
    return {"message": "Deletion command created", "filename": filename}


@router.post("/commands/send")
def send_command(authorized: bool = Depends(auth_admin)):
    return {"message": "Command queued"}
