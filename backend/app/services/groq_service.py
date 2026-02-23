from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

MODEL_NAME = "llama-3.1-8b-instant" # Faster model with higher rate limits

async def generate_response(prompt: str, system_prompt: str = "You are a helpful learning assistant.", json_mode: bool = False) -> str:
    """Generate a text response using Groq LLM."""
    try:
        kwargs = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
        }
        
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        completion = client.chat.completions.create(**kwargs)
        return completion.choices[0].message.content
    except Exception as e:
        error_str = str(e).lower()
        if "rate_limit" in error_str or "429" in error_str:
            raise ValueError("Groq rate limit reached. Please wait a moment and try again.")
        raise e
