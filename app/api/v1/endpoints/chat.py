from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.api.v1.schemas.chat import ChatCompletionRequest, ChatCompletionResponse
from app.domains.vllm_service import vllm_client
from app.core.exceptions import VllmTimeoutError, VllmUnavailableError
from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    authorization: Optional[str] = Header(None),
):
    # Simple API key auth
    expected = f"Bearer {settings.API_KEY}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    payload = request.model_dump()
    try:
        result = await vllm_client.chat_completion(payload)
        return result
    except VllmTimeoutError as e:
        logger.error("vllm_timeout", extra={"error": str(e)})
        raise HTTPException(status_code=504, detail="Model inference timed out")
    except VllmUnavailableError as e:
        logger.error("vllm_unavailable", extra={"error": str(e)})
        raise HTTPException(status_code=503, detail="Model service unavailable")
    except Exception as e:
        logger.error("unexpected_error", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")
