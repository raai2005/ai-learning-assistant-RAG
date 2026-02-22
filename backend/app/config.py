from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "AI Learning Assistant API"
    DEBUG: bool = True

    # Frontend origin for CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Gemini
    GEMINI_API_KEY: str = ""

    # Pinecone
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "ai-learning-assistant"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
