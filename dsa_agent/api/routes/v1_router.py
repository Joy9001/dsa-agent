from fastapi import APIRouter

from api.routes.agent import agent_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(agent_router)
