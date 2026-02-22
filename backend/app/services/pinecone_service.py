from pinecone import Pinecone

from app.config import settings

# Initialize Pinecone client
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)


async def upsert_chunks(
    content_id: str, chunks: list[str], embeddings: list[list[float]]
) -> int:
    """Upsert chunk vectors into Pinecone with metadata."""
    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vectors.append(
            {
                "id": f"{content_id}_{i}",
                "values": embedding,
                "metadata": {
                    "content_id": content_id,
                    "chunk_index": i,
                    "text": chunk,
                },
            }
        )

    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        index.upsert(vectors=batch)

    return len(vectors)


async def query_similar(
    query_embedding: list[float], content_id: str, top_k: int = 5
) -> list[dict]:
    """Query Pinecone for similar chunks within a specific content."""
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={"content_id": {"$eq": content_id}},
    )

    return [
        {
            "text": match.metadata.get("text", ""),
            "chunk_index": match.metadata.get("chunk_index", 0),
            "score": match.score,
        }
        for match in results.matches
    ]


async def fetch_all_chunks(content_id: str) -> list[str]:
    """Fetch all chunks for a content_id by querying with a dummy vector."""
    # Use a zero vector to match all, filtered by content_id
    dummy_vector = [0.0] * 768
    results = index.query(
        vector=dummy_vector,
        top_k=1000,
        include_metadata=True,
        filter={"content_id": {"$eq": content_id}},
    )

    # Sort by chunk_index and return texts
    sorted_matches = sorted(
        results.matches, key=lambda m: m.metadata.get("chunk_index", 0)
    )
    return [match.metadata.get("text", "") for match in sorted_matches]
