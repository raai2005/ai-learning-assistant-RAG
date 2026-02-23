from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "AI Learning Assistant API"
    DEBUG: bool = True

    # Frontend origin for CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Gemini
    GEMINI_API_KEY: str = ""

    # Groq
    GROQ_API_KEY: str = ""

    # Hugging Face (Optional, but recommended for speed)
    HUGGINGFACE_API_KEY: str = ""

    # Pinecone
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "ai-learning-assistant"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # Embedding Model (Local)
    EMBEDDING_MODEL_NAME: str = "all-distilroberta-v1"
    TRANSFORMERS_CACHE: str = "D:\\ai_models\\huggingface"

    class Config:
        env_file = ".env"
        extra = "allow" # Allow extra fields for flexibility


settings = Settings()
