from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks

from app.schemas import ProcessPdfResponse
from app.services import embedding_service, pinecone_service, supabase_service, processor

router = APIRouter()

async def run_background_process(content_id: str, file_contents: bytes):
    """Heavy lifting background task: Chunks -> Embeddings -> Vector DB."""
    try:
        # 1. Extract text and Chunk
        text, pages_count = processor.extract_pdf_text(file_contents)
        chunks = processor.chunk_text(text)
        
        # Max limit for free tier stability
        if len(chunks) > 500:
            chunks = chunks[:500]

        # 2. Embed
        embeddings = await embedding_service.embed_chunks(chunks)

        # 3. Upsert to Pinecone (Includes durability wait)
        await pinecone_service.upsert_chunks(content_id, chunks, embeddings)

        # 4. Mark as DONE
        await supabase_service.update_content(content_id, len(chunks), "processed")
        print(f"SUCCESS: Background processing complete for: {content_id}")

    except Exception as e:
        print(f"CRITICAL ERROR: Background process failed for {content_id}: {str(e)}")
        await supabase_service.update_content(content_id, status="failed", error_message=str(e))


@router.post(
    "/process-pdf",
    response_model=ProcessPdfResponse,
    summary="Process a PDF document (Background)",
    description="Starts a background job to process the PDF. Returns the content ID immediately.",
)
async def process_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)

    if file_size_mb > 25:
        raise HTTPException(status_code=400, detail="File too large (Max 25MB).")

    # 1. Create Initial Entry in Supabase (Status: Processing)
    content = await supabase_service.create_content(
        content_type="pdf",
        source=file.filename or "unknown.pdf",
        title=file.filename or "unknown.pdf",
        metadata={"file_size_mb": round(file_size_mb, 2)},
    )
    content_id = content["id"]

    # 2. Add to Background Tasks
    background_tasks.add_task(run_background_process, content_id, contents)

    # 3. Return Instant Response
    return ProcessPdfResponse(
        content_id=content_id,
        filename=file.filename or "unknown.pdf",
        pages_count=0, # Will be updated in background
        chunks_count=0, # Will be updated in background
        status="processing",
        created_at=content["created_at"],
    )
