from fastapi import APIRouter, HTTPException

from app.schemas import ChatRequest, ChatResponse
from app.services import embedding_service, groq_service, pinecone_service, supabase_service

router = APIRouter()

CHAT_PROMPT = """You are an expert academic tutor and study assistant. Your goal is to help the user understand the content deeply.

RULES:
1. Use ONLY the provided context to answer. If the answer isn't there, say you don't know based on the material.
2. Format your response using clean Markdown.
3. Use bullet points, bold text, and numbered lists to make the information easy to digest.
4. If the user asks for "basic questions" or a "summary", provide a well-structured list.
5. Keep a professional, encouraging tone.

Context:
{context}

User's Question: {question}

Response:"""


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with processed content",
    description="Embeds the user's question, searches Pinecone for relevant chunks, and uses Gemini LLM to generate an answer based on the retrieved context (RAG).",
)
async def chat(request: ChatRequest):
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
        # 1. Embed the user's question
        embedding_list = await embedding_service.get_embeddings(request.message)
        query_embedding = embedding_list[0]

        # 2. Search Pinecone for relevant chunks
        similar_chunks = await pinecone_service.query_similar(
            query_embedding=query_embedding,
            content_id=request.content_id,
            top_k=5,
        )

        if not similar_chunks:
            return ChatResponse(
                content_id=request.content_id,
                reply="I couldn't find any relevant information in the content to answer your question.",
                sources=[],
            )

        # 3. Build context from retrieved chunks
        context = "\n\n".join([chunk["text"] for chunk in similar_chunks])
        sources = [f"chunk_{chunk['chunk_index']}" for chunk in similar_chunks]

        # 4. Generate answer via Groq (using the high-performance model for chat)
        prompt = CHAT_PROMPT.format(context=context, question=request.message)
        reply = await groq_service.generate_response(prompt, model_override="llama-3.3-70b-versatile")

        return ChatResponse(
            content_id=request.content_id,
            reply=reply,
            sources=sources,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
