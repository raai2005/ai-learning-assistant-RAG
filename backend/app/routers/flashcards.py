import json

from fastapi import APIRouter, HTTPException

from app.schemas import (
    GenerateFlashcardsRequest,
    GenerateFlashcardsResponse,
    Flashcard,
)
from app.services import groq_service, pinecone_service, supabase_service

router = APIRouter()

FLASHCARD_PROMPT = """You are an expert educator. Based on the following content, generate exactly {num_cards} flashcards for studying.

Each flashcard should have a clear question and a concise answer.

Return a JSON object with a key "flashcards" containing an array of objects.
Each object must have "question" and "answer" keys.

Example format:
{{
  "flashcards": [
    {{"question": "What is X?", "answer": "X is..."}},
    {{"question": "How does Y work?", "answer": "Y works by..."}}
  ]
}}

Content:
{content}
"""


@router.post(
    "/generate-flashcards",
    response_model=GenerateFlashcardsResponse,
    summary="Generate flashcards from processed content",
    description="Retrieves content chunks from Pinecone and uses Gemini LLM to generate study flashcards.",
)
async def generate_flashcards(request: GenerateFlashcardsRequest):
    # Verify content exists and is processed
    content = await supabase_service.get_content(request.content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if content["status"] == "processing":
        raise HTTPException(status_code=400, detail="Content is still being processed. Please try again in a few moments.")
    
    if content["status"] == "failed":
        error_info = content.get("metadata", {}).get("error", "Unknown error")
        raise HTTPException(status_code=400, detail=f"Content processing failed: {error_info}")

    try:
        # 1. Fetch all chunks from Pinecone
        chunks = await pinecone_service.fetch_all_chunks(request.content_id)

        if not chunks:
            if content["status"] == "processed":
                 raise HTTPException(status_code=404, detail="No chunks found. The content may have been too short or empty.")
            raise HTTPException(status_code=404, detail="No chunks found for this content")

        # 2. Combine chunks into context (Limit to 20 chunks for speed and API safety)
        if len(chunks) > 20:
            chunks = chunks[:20]
        combined_content = "\n\n".join(chunks)

        # 3. Generate flashcards via Groq (using JSON mode)
        num_cards = request.num_cards or 10
        prompt = FLASHCARD_PROMPT.format(num_cards=num_cards, content=combined_content)
        response = await groq_service.generate_response(prompt, json_mode=True)

        # 4. Parse JSON response
        data = json.loads(response)
        flashcards_data = data.get("flashcards", [])

        flashcards = [
            Flashcard(id=i + 1, question=fc["question"], answer=fc["answer"])
            for i, fc in enumerate(flashcards_data)
        ]

        return GenerateFlashcardsResponse(
            content_id=request.content_id,
            flashcards=flashcards,
            total=len(flashcards),
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse flashcards from AI response")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate flashcards: {str(e)}")
