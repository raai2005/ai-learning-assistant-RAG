from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import HealthResponse
from app.routers import video, pdf, flashcards, quiz, chat

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for AI Learning Assistant — process videos & PDFs, generate flashcards & quizzes, and chat with your content using RAG.",
    version="0.1.0",
)

# ── CORS ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────
app.include_router(video.router, prefix="/api", tags=["Video"])
app.include_router(pdf.router, prefix="/api", tags=["PDF"])
app.include_router(flashcards.router, prefix="/api", tags=["Flashcards"])
app.include_router(quiz.router, prefix="/api", tags=["Quiz"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])


# ── Health Check ──────────────────────────────
@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
    )
