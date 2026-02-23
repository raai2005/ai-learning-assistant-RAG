from fastapi import APIRouter, HTTPException

from app.schemas import ChatRequest, ChatResponse
from app.services import gemini, pinecone_service, supabase_service

router = APIRouter()

CHAT_PROMPT = """You are a helpful AI learning assistant. Answer the user's question based ONLY on the provided context. If the context doesn't contain enough information to answer, say so honestly.

Context:
{context}

User's Question: {question}

Provide a clear, concise, and helpful answer:"""


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
        # 1. Embed the user's question (using retry-enabled function)
        embedding_list = await gemini.get_embeddings_with_retry(request.message)
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

        # 4. Generate answer via Gemini
        prompt = CHAT_PROMPT.format(context=context, question=request.message)
        reply = await gemini.generate_response(prompt)

        return ChatResponse(
            content_id=request.content_id,
            reply=reply,
            sources=sources,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
