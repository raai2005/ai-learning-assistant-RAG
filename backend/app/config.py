from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "AI Learning Assistant API"
    DEBUG: bool = True

    # Frontend origin for CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Future: add API keys, DB URLs, etc.
    # OPENAI_API_KEY: str = ""
    # GEMINI_API_KEY: str = ""
    # CHROMA_PERSIST_DIR: str = "./chroma_data"

    class Config:
        env_file = ".env"


settings = Settings()
