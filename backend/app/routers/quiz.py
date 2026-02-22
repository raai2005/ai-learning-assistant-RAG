from fastapi import APIRouter

from app.schemas import (
    GenerateQuizRequest,
    GenerateQuizResponse,
    QuizQuestion,
    QuizOption,
)

router = APIRouter()


@router.post(
    "/generate-quiz",
    response_model=GenerateQuizResponse,
    summary="Generate a quiz from processed content",
    description="Takes a content_id and generates multiple-choice questions. In production, this will retrieve chunks from the vector DB and use an LLM to create quiz questions.",
)
async def generate_quiz(request: GenerateQuizRequest):
    # TODO: Replace with real RAG logic
    # 1. Retrieve chunks for content_id from ChromaDB
    # 2. Send chunks to LLM with quiz generation prompt
    # 3. Parse LLM response into QuizQuestion objects

    num = request.num_questions or 5

    mock_questions = [
        QuizQuestion(
            id=i + 1,
            question=f"Sample quiz question {i + 1}?",
            options=[
                QuizOption(label="A", text="Option A"),
                QuizOption(label="B", text="Option B"),
                QuizOption(label="C", text="Option C"),
                QuizOption(label="D", text="Option D"),
            ],
            correct_answer="A",
        )
        for i in range(num)
    ]

    return GenerateQuizResponse(
        content_id=request.content_id,
        questions=mock_questions,
        total=len(mock_questions),
    )
