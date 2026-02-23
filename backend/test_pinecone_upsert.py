import asyncio
from app.services import pinecone_service

async def main():
    try:
        content_id = "test_id_567"
        chunks = ["This is a test chunk"]
        embeddings = [[0.1] * 768]
        await pinecone_service.upsert_chunks(content_id, chunks, embeddings)
        
        print("Wait for 2 seconds for consistency...")
        await asyncio.sleep(2)
        
        fetch_results = pinecone_service.index.fetch(ids=[f"{content_id}_0"])
        if f"{content_id}_0" in fetch_results.vectors:
            print("SUCCESS: Found the test vector!")
        else:
            print(f"FAILURE: Vector not found. results: {fetch_results.vectors.keys()}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
