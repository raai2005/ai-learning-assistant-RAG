from fastapi import APIRouter

from app.schemas import (
    GenerateFlashcardsRequest,
    GenerateFlashcardsResponse,
    Flashcard,
)

router = APIRouter()


@router.post(
    "/generate-flashcards",
    response_model=GenerateFlashcardsResponse,
    summary="Generate flashcards from processed content",
    description="Takes a content_id and generates flashcards. In production, this will retrieve chunks from the vector DB and use an LLM to create Q&A flashcards.",
)
async def generate_flashcards(request: GenerateFlashcardsRequest):
    # TODO: Replace with real RAG logic
    # 1. Retrieve chunks for content_id from ChromaDB
    # 2. Send chunks to LLM with flashcard generation prompt
    # 3. Parse LLM response into Flashcard objects

    num = request.num_cards or 10

    mock_flashcards = [
        Flashcard(
            id=i + 1,
            question=f"Sample question {i + 1} about the content?",
            answer=f"This is the answer to question {i + 1}.",
        )
        for i in range(num)
    ]

    return GenerateFlashcardsResponse(
        content_id=request.content_id,
        flashcards=mock_flashcards,
        total=len(mock_flashcards),
    )
