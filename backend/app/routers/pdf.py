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

        # 4. Generate embeddings via Gemini
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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
