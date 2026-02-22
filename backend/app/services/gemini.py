from google import genai
from google.genai import types

from app.config import settings

# Initialize the Gemini client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"
LLM_MODEL = "gemini-2.0-flash"
EMBEDDING_DIMENSION = 768  # Must match Pinecone index dimension


async def get_embeddings(text: str) -> list[float]:
    """Generate embeddings for a text string using Gemini."""
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSION,
        ),
    )
    return response.embeddings[0].values


async def generate_response(prompt: str) -> str:
    """Generate a text response using Gemini LLM."""
    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
    )
    return response.text


async def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple chunks."""
    embeddings = []
    for chunk in chunks:
        embedding = await get_embeddings(chunk)
        embeddings.append(embedding)
    return embeddings

