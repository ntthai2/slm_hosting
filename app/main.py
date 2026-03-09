from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.router import router as v1_router
from app.domains.vllm_service import vllm_client
from app.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — connecting to vLLM...")
    await vllm_client.start()
    yield
    logger.info("Shutting down — closing vLLM client...")
    await vllm_client.stop()


app = FastAPI(
    title="SLM Hosting — API Wrapper",
    description="Production-ready FastAPI wrapper around vLLM",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(v1_router)


@app.get("/")
async def root():
    return {"message": "SLM Hosting API is running", "docs": "/docs"}
