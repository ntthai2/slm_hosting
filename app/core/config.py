from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    VLLM_URL: str = "http://vllm:8000"
    MODEL_NAME: str = "models/Qwen2.5-1.5B-Instruct-AWQ"
    LOG_LEVEL: str = "INFO"
    REQUEST_TIMEOUT: float = 30.0
    MAX_TOKENS_DEFAULT: int = 512
    API_KEY: str = "secret-key-change-me"

    class Config:
        env_file = ".env"


settings = Settings()
