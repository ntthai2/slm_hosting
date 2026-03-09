from fastapi import APIRouter
from app.api.v1.endpoints import chat, health

router = APIRouter(prefix="/v1")
router.include_router(chat.router)
router.include_router(health.router)
