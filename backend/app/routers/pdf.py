import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.schemas import ProcessPdfResponse

router = APIRouter()


@router.post(
    "/process-pdf",
    response_model=ProcessPdfResponse,
    summary="Process a PDF document",
    description="Accepts a PDF file upload. In production, this will extract text, chunk it, generate embeddings, and store in the vector DB.",
)
async def process_pdf(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Received: " + (file.content_type or "unknown"),
        )

    # Read file content (for future processing)
    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)

    if file_size_mb > 25:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({file_size_mb:.1f}MB). Maximum is 25MB.",
        )

    # TODO: Replace with real RAG logic
    # 1. PyPDF2 / pdfplumber → extract text
    # 2. Split text into chunks
    # 3. Generate embeddings (Gemini / OpenAI)
    # 4. Store in ChromaDB with content_id

    content_id = str(uuid.uuid4())

    return ProcessPdfResponse(
        content_id=content_id,
        filename=file.filename or "unknown.pdf",
        pages_count=12,
        chunks_count=36,
        status="processed",
        created_at=datetime.now(timezone.utc),
    )
