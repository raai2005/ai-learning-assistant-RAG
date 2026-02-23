from supabase import create_client

from app.config import settings

# Initialize Supabase client
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

TABLE_NAME = "contents"


async def create_content(
    content_type: str,
    source: str,
    title: str | None = None,
    metadata: dict | None = None,
) -> dict:
    """Insert a new content record into Supabase."""
    data = {
        "content_type": content_type,
        "source": source,
        "title": title or "",
        "metadata": metadata or {},
        "status": "processing",
    }

    result = supabase.table(TABLE_NAME).insert(data).execute()
    return result.data[0]


async def update_content(
    content_id: str, 
    chunks_count: int | None = None, 
    status: str = "processed",
    error_message: str | None = None
) -> dict:
    """Update content record after processing."""
    update_data = {"status": status}
    if chunks_count is not None:
        update_data["chunks_count"] = chunks_count
    if error_message:
        update_data["metadata"] = {"error": error_message}
        
    result = (
        supabase.table(TABLE_NAME)
        .update(update_data)
        .eq("id", content_id)
        .execute()
    )
    return result.data[0]


async def get_content(content_id: str) -> dict | None:
    """Fetch a content record by ID."""
    result = (
        supabase.table(TABLE_NAME)
        .select("*")
        .eq("id", content_id)
        .execute()
    )
    return result.data[0] if result.data else None
