import os
import httpx
import asyncio
from app.config import settings

# Set the cache directory before importing sentence_transformers
os.environ["TRANSFORMERS_CACHE"] = settings.TRANSFORMERS_CACHE

# Lasy load the model only if needed to save memory if using API
_local_model = None

def get_local_model():
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        _local_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _local_model

async def get_embeddings(text_or_list: str | list[str]) -> list[list[float]]:
    """Generate embeddings using Hugging Face API (Cloud) with Local Fallback."""
    if isinstance(text_or_list, str):
        text_or_list = [text_or_list]

    # 1. Try Hugging Face API first (Speed boost)
    if settings.HUGGINGFACE_API_KEY:
        try:
            api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{settings.EMBEDDING_MODEL_NAME}"
            headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_url, 
                    headers=headers, 
                    json={"inputs": text_or_list, "options": {"wait_for_model": True}},
                    timeout=30.0
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            print(f"HF API Failed, falling back to local: {e}")

    # 2. Local Fallback (Standard)
    model = get_local_model()
    # Run in thread pool to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    embeddings = await loop.run_in_executor(None, lambda: model.encode(text_or_list))
    return embeddings.tolist()

async def embed_chunks(chunks: list[str], batch_size: int = 50) -> list[list[float]]:
    """Generate embeddings for multiple chunks efficiently."""
    return await get_embeddings(chunks)
