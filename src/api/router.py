from fastapi import APIRouter
from src.api import admin, agent
from src.config import settings

api_router = APIRouter(prefix=settings.API_VERSION)
api_router.include_router(agent.router)
api_router.include_router(admin.router)
