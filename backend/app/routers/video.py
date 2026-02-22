from fastapi import APIRouter, HTTPException

from app.schemas import ProcessVideoRequest, ProcessVideoResponse
from app.services import gemini, pinecone_service, supabase_service, processor

router = APIRouter()


@router.post(
    "/process-video",
    response_model=ProcessVideoResponse,
    summary="Process a YouTube video",
    description="Downloads the transcript, chunks it, generates Gemini embeddings, stores vectors in Pinecone, and saves metadata in Supabase.",
)
async def process_video(request: ProcessVideoRequest):
    try:
        # 1. Get transcript from YouTube
        transcript = processor.get_youtube_transcript(request.youtube_url)
        title = processor.get_youtube_title(request.youtube_url)

        # 2. Create content record in Supabase
        content = await supabase_service.create_content(
            content_type="video",
            source=request.youtube_url,
            title=title,
        )
        content_id = content["id"]

        # 3. Chunk the transcript
        chunks = processor.chunk_text(transcript)

        # 4. Generate embeddings via Gemini
        embeddings = await gemini.embed_chunks(chunks)

        # 5. Upsert into Pinecone
        await pinecone_service.upsert_chunks(content_id, chunks, embeddings)

        # 6. Update Supabase with chunk count + status
        await supabase_service.update_content(content_id, len(chunks), "processed")

        return ProcessVideoResponse(
            content_id=content_id,
            title=title,
            duration=None,
            chunks_count=len(chunks),
            status="processed",
            created_at=content["created_at"],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")
