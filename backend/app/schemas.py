from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ──────────────────────────────────────
# Process Video
# ──────────────────────────────────────

class ProcessVideoRequest(BaseModel):
    youtube_url: str = Field(
        ...,
        description="Full YouTube video URL",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcY"],
    )


class ProcessVideoResponse(BaseModel):
    content_id: str
    title: str
    duration: Optional[str] = None
    chunks_count: int
    status: str
    created_at: datetime


# ──────────────────────────────────────
# Process PDF
# ──────────────────────────────────────

class ProcessPdfResponse(BaseModel):
    content_id: str
    filename: str
    pages_count: int
    chunks_count: int
    status: str
    created_at: datetime


# ──────────────────────────────────────
# Generate Flashcards
# ──────────────────────────────────────

class GenerateFlashcardsRequest(BaseModel):
    content_id: str = Field(..., description="ID of the processed content")
    num_cards: Optional[int] = Field(
        10, description="Number of flashcards to generate", ge=1, le=50
    )


class Flashcard(BaseModel):
    id: int
    question: str
    answer: str


class GenerateFlashcardsResponse(BaseModel):
    content_id: str
    flashcards: list[Flashcard]
    total: int


# ──────────────────────────────────────
# Generate Quiz
# ──────────────────────────────────────

class GenerateQuizRequest(BaseModel):
    content_id: str = Field(..., description="ID of the processed content")
    num_questions: Optional[int] = Field(
        5, description="Number of quiz questions", ge=1, le=20
    )


class QuizOption(BaseModel):
    label: str
    text: str


class QuizQuestion(BaseModel):
    id: int
    question: str
    options: list[QuizOption]
    correct_answer: str


class GenerateQuizResponse(BaseModel):
    content_id: str
    questions: list[QuizQuestion]
    total: int


# ──────────────────────────────────────
# Chat
# ──────────────────────────────────────

class ChatRequest(BaseModel):
    content_id: str = Field(..., description="ID of the processed content")
    message: str = Field(..., description="User message / question", min_length=1)


class ChatResponse(BaseModel):
    content_id: str
    reply: str
    sources: list[str] = Field(
        default_factory=list,
        description="Chunk references used to generate the reply",
    )


# ──────────────────────────────────────
# Health
# ──────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    app_name: str
