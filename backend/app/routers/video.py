import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas import ProcessVideoRequest, ProcessVideoResponse

router = APIRouter()


@router.post(
    "/process-video",
    response_model=ProcessVideoResponse,
    summary="Process a YouTube video",
    description="Accepts a YouTube URL. In production, this will download the transcript, chunk it, generate embeddings, and store in the vector DB.",
)
async def process_video(request: ProcessVideoRequest):
    # TODO: Replace with real RAG logic
    # 1. youtube-transcript-api → get transcript
    # 2. Split transcript into chunks
    # 3. Generate embeddings (Gemini / OpenAI)
    # 4. Store in ChromaDB with content_id

    content_id = str(uuid.uuid4())

    return ProcessVideoResponse(
        content_id=content_id,
        title="Sample Video Title",
        duration="10:30",
        chunks_count=24,
        status="processed",
        created_at=datetime.now(timezone.utc),
    )
