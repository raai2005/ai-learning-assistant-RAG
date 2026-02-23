import asyncio
from app.services import pinecone_service
import sys

async def main():
    if len(sys.argv) < 2:
        print("Usage status_check.py <content_id>")
        return
    
    content_id = sys.argv[1]
    print(f"Checking Pinecone for content_id: {content_id}")
    
    try:
        # Try dummy search first
        zero_vector = [0.0] * 768
        results = pinecone_service.index.query(
            vector=zero_vector,
            top_k=5,
            include_metadata=True,
            filter={"content_id": {"$eq": content_id}}
        )
        print(f"Found {len(results.matches)} matches via query.")
        for match in results.matches:
            print(f" - ID: {match.id}, Metadata content_id: {match.metadata.get('content_id')}")
            
        # Try direct fetch for ID _0
        first_id = f"{content_id}_0"
        print(f"Trying to fetch specific ID: {first_id}")
        fetch_results = pinecone_service.index.fetch(ids=[first_id])
        print(f"Fetch results: {fetch_results}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
