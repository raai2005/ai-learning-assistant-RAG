import asyncio
import time
from google import genai
from google.genai import types

from app.config import settings

# Initialize the Gemini client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"
LLM_MODEL = "gemini-2.0-flash"
EMBEDDING_DIMENSION = 768  # Must match Pinecone index dimension


async def get_embeddings_with_retry(text_or_list: str | list[str], retries: int = 5, base_delay: float = 1.0) -> list[list[float]]:
    """Generate embeddings with exponential backoff for rate limits."""
    for i in range(retries):
        try:
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text_or_list,
                config=types.EmbedContentConfig(
                    output_dimensionality=EMBEDDING_DIMENSION,
                ),
            )
            # If it's a single string, response.embeddings is a list of 1
            # If it's a list, response.embeddings matches the list length
            return [emb.values for emb in response.embeddings]
        except Exception as e:
            # Check for Rate Limit (429) or Service Unavailable (503)
            error_str = str(e).lower()
            if ("429" in error_str or "resource_exhausted" in error_str or "503" in error_str) and i < retries - 1:
                delay = base_delay * (2 ** i)
                await asyncio.sleep(delay)
                continue
            raise e
    return []


async def generate_response(prompt: str) -> str:
    """Generate a text response using Gemini LLM."""
    try:
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "resource_exhausted" in error_str:
            raise ValueError("AI rate limit reached. Please wait a minute and try again.")
        raise e


async def embed_chunks(chunks: list[str], batch_size: int = 50) -> list[list[float]]:
    """Generate embeddings for multiple chunks in batches."""
    all_embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        batch_embeddings = await get_embeddings_with_retry(batch)
        all_embeddings.extend(batch_embeddings)
        # Small delay between batches to stay under free tier RPM
        if i + batch_size < len(chunks):
            await asyncio.sleep(0.5)
    return all_embeddings

