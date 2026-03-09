from pydantic import BaseModel
from typing import Optional


class HealthResponse(BaseModel):
    status: str          # "ok" | "degraded" | "error"
    model_loaded: bool
    vllm_url: str
    detail: Optional[str] = None
