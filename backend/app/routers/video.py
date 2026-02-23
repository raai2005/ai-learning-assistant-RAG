from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.schemas import ProcessVideoRequest, ProcessVideoResponse
from app.services import embedding_service, pinecone_service, supabase_service, processor

router = APIRouter()

async def run_background_video_process(content_id: str, youtube_url: str):
    """Background task for videos: Transcript -> Embeddings -> Vector DB."""
    try:
        # 1. Fetch transcript and title
        transcript = processor.get_youtube_transcript(youtube_url)
        chunks = processor.chunk_text(transcript)
        
        # Max limit for stability
        if len(chunks) > 500:
            chunks = chunks[:500]

        # 2. Embed
        embeddings = await embedding_service.embed_chunks(chunks)

        # 3. Upsert to Pinecone (Includes durability wait)
        await pinecone_service.upsert_chunks(content_id, chunks, embeddings)

        # 4. Mark as DONE
        await supabase_service.update_content(content_id, len(chunks), "processed")
        print(f"SUCCESS: Video processing complete for: {content_id}")

    except Exception as e:
        print(f"CRITICAL ERROR: Video background process failed for {content_id}: {str(e)}")
        await supabase_service.update_content(content_id, status="failed", error_message=str(e))


@router.post(
    "/process-video",
    response_model=ProcessVideoResponse,
    summary="Process a YouTube video (Background)",
    description="Starts a background job to fetch transcript and process. Returns the content ID immediately.",
)
async def process_video(request: ProcessVideoRequest, background_tasks: BackgroundTasks):
    # Get title quickly (or use a placeholder) to create record
    try:
        title = processor.get_youtube_title(request.youtube_url)
    except:
        title = "YouTube Video"

    # 1. Create Initial Entry
    content = await supabase_service.create_content(
        content_type="video",
        source=request.youtube_url,
        title=title,
    )
    content_id = content["id"]

    # 2. Add to Background Tasks
    background_tasks.add_task(run_background_video_process, content_id, request.youtube_url)

    # 3. Return Instant Response
    return ProcessVideoResponse(
        content_id=content_id,
        title=title,
        duration=None,
        chunks_count=0,
        status="processing",
        created_at=content["created_at"],
    )
