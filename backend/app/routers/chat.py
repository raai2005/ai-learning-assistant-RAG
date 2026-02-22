from fastapi import APIRouter

from app.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with processed content",
    description="Send a message/question about processed content. In production, this will embed the query, search the vector DB for relevant chunks, and use an LLM to generate an answer.",
)
async def chat(request: ChatRequest):
    # TODO: Replace with real RAG logic
    # 1. Embed user message (Gemini / OpenAI embeddings)
    # 2. Search ChromaDB for top-k similar chunks
    # 3. Build prompt: system context + retrieved chunks + user message
    # 4. Send to LLM and return response

    return ChatResponse(
        content_id=request.content_id,
        reply=f'This is a mock response to your question: "{request.message}". '
        "In production, this will use RAG to retrieve relevant content and generate an AI-powered answer.",
        sources=["chunk_1", "chunk_3", "chunk_7"],
    )
