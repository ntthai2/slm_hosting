import httpx
import time
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import VllmTimeoutError, VllmUnavailableError

logger = get_logger(__name__)


class VllmClient:
    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def start(self):
        self._client = httpx.AsyncClient(
            base_url=settings.VLLM_URL,
            timeout=settings.REQUEST_TIMEOUT,
        )
        logger.info("VllmClient started", extra={"vllm_url": settings.VLLM_URL})

    async def stop(self):
        if self._client:
            await self._client.aclose()
            logger.info("VllmClient closed")

    async def chat_completion(self, payload: dict) -> dict:
        # Enforce model name & max_tokens cap
        payload["model"] = settings.MODEL_NAME
        payload.setdefault("max_tokens", settings.MAX_TOKENS_DEFAULT)
        payload["max_tokens"] = min(payload["max_tokens"], settings.MAX_TOKENS_DEFAULT)

        start = time.perf_counter()
        try:
            resp = await self._client.post("/v1/chat/completions", json=payload)
            resp.raise_for_status()
            latency_ms = (time.perf_counter() - start) * 1000
            data = resp.json()
            usage = data.get("usage", {})
            logger.info(
                "chat_completion ok",
                extra={
                    "latency_ms": round(latency_ms, 2),
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "model": settings.MODEL_NAME,
                },
            )
            return data
        except httpx.TimeoutException as e:
            raise VllmTimeoutError(f"vLLM timeout after {settings.REQUEST_TIMEOUT}s") from e
        except httpx.ConnectError as e:
            raise VllmUnavailableError("Cannot connect to vLLM") from e

    async def health(self) -> bool:
        """Return True only when vLLM /health returns 200."""
        try:
            resp = await self._client.get("/health", timeout=5.0)
            return resp.status_code == 200
        except Exception:
            return False


# Singleton
vllm_client = VllmClient()
