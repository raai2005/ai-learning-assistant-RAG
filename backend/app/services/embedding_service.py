import os
from app.config import settings

# Set the cache directory before importing sentence_transformers
os.environ["TRANSFORMERS_CACHE"] = settings.TRANSFORMERS_CACHE

from sentence_transformers import SentenceTransformer

# Initialize the model
# Using all-mpnet-base-v2 (768 dimensions) to match original Pinecone index
model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

async def get_embeddings(text_or_list: str | list[str]) -> list[list[float]]:
    """Generate embeddings using the local sentence-transformer model."""
    if isinstance(text_or_list, str):
        text_or_list = [text_or_list]
    
    # model.encode is synchronous, but we can run it in a thread or just call it
    # For small batches, it's fast enough.
    embeddings = model.encode(text_or_list)
    return embeddings.tolist()

async def embed_chunks(chunks: list[str], batch_size: int = 50) -> list[list[float]]:
    """Generate embeddings for multiple chunks."""
    # sentence-transformers' encode handles batching internally and efficiently
    embeddings = model.encode(chunks, batch_size=batch_size, show_progress_bar=False)
    return embeddings.tolist()
