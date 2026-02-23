from fastapi import APIRouter, File, UploadFile, HTTPException

from app.schemas import ProcessPdfResponse
from app.services import gemini, pinecone_service, supabase_service, processor

router = APIRouter()


@router.post(
    "/process-pdf",
    response_model=ProcessPdfResponse,
    summary="Process a PDF document",
    description="Extracts text from PDF, chunks it, generates Gemini embeddings, stores vectors in Pinecone, and saves metadata in Supabase.",
)
async def process_pdf(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Received: " + (file.content_type or "unknown"),
        )

    # Read file content
    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)

    if file_size_mb > 25:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({file_size_mb:.1f}MB). Maximum is 25MB.",
        )

    content_id = None
    try:
        # 1. Extract text from PDF
        text, pages_count = processor.extract_pdf_text(contents)

        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF. The file may be scanned or image-based.")

        # 2. Create content record in Supabase
        content = await supabase_service.create_content(
            content_type="pdf",
            source=file.filename or "unknown.pdf",
            title=file.filename or "unknown.pdf",
            metadata={"pages_count": pages_count, "file_size_mb": round(file_size_mb, 2)},
        )
        content_id = content["id"]

        # 3. Chunk the text
        chunks = processor.chunk_text(text)
        
        # Free Tier Safety Limit: Max 200 chunks per PDF
        if len(chunks) > 200:
            chunks = chunks[:200]

        # 4. Generate embeddings via Gemini (now batched and retried)
        embeddings = await gemini.embed_chunks(chunks)

        # 5. Upsert into Pinecone
        await pinecone_service.upsert_chunks(content_id, chunks, embeddings)

        # 6. Update Supabase with chunk count + status
        await supabase_service.update_content(content_id, len(chunks), "processed")

        return ProcessPdfResponse(
            content_id=content_id,
            filename=file.filename or "unknown.pdf",
            pages_count=pages_count,
            chunks_count=len(chunks),
            status="processed",
            created_at=content["created_at"],
        )

    except Exception as e:
        error_msg = str(e)
        if content_id:
            await supabase_service.update_content(content_id, status="failed", error_message=error_msg)
            
        if isinstance(e, HTTPException):
            raise e
        if isinstance(e, ValueError):
            raise HTTPException(status_code=400, detail=error_msg)
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {error_msg}")
