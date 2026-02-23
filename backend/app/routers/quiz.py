import json

from fastapi import APIRouter, HTTPException

from app.schemas import (
    GenerateQuizRequest,
    GenerateQuizResponse,
    QuizQuestion,
    QuizOption,
)
from app.services import gemini, pinecone_service, supabase_service

router = APIRouter()

QUIZ_PROMPT = """You are an expert educator. Based on the following content, generate exactly {num_questions} multiple-choice quiz questions.

Each question should have 4 options (A, B, C, D) with exactly one correct answer.

Return ONLY a valid JSON array of objects. No markdown, no explanation, just the JSON array.

Each object should have:
- "question": the question text
- "options": array of objects with "label" (A/B/C/D) and "text"
- "correct_answer": the label of the correct option (A, B, C, or D)

Example format:
[
  {{
    "question": "What is X?",
    "options": [
      {{"label": "A", "text": "Option 1"}},
      {{"label": "B", "text": "Option 2"}},
      {{"label": "C", "text": "Option 3"}},
      {{"label": "D", "text": "Option 4"}}
    ],
    "correct_answer": "A"
  }}
]

Content:
{content}
"""


@router.post(
    "/generate-quiz",
    response_model=GenerateQuizResponse,
    summary="Generate a quiz from processed content",
    description="Retrieves content chunks from Pinecone and uses Gemini LLM to generate a multiple-choice quiz.",
)
async def generate_quiz(request: GenerateQuizRequest):
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

        # 2. Combine chunks into context
        combined_content = "\n\n".join(chunks)

        # 3. Generate quiz via Gemini
        num_questions = request.num_questions or 5
        prompt = QUIZ_PROMPT.format(num_questions=num_questions, content=combined_content)
        response = await gemini.generate_response(prompt)

        # 4. Parse JSON response
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        quiz_data = json.loads(cleaned)

        questions = [
            QuizQuestion(
                id=i + 1,
                question=q["question"],
                options=[QuizOption(label=o["label"], text=o["text"]) for o in q["options"]],
                correct_answer=q["correct_answer"],
            )
            for i, q in enumerate(quiz_data)
        ]

        return GenerateQuizResponse(
            content_id=request.content_id,
            questions=questions,
            total=len(questions),
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse quiz from AI response")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")
