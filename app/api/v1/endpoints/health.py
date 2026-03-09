from fastapi import APIRouter
from app.api.v1.schemas.health import HealthResponse
from app.domains.vllm_service import vllm_client
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    model_loaded = await vllm_client.health()
    return HealthResponse(
        status="ok" if model_loaded else "degraded",
        model_loaded=model_loaded,
        vllm_url=settings.VLLM_URL,
        detail=None if model_loaded else "vLLM is not responding",
    )
