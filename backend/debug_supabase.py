import asyncio
from app.services import supabase_service

async def main():
    try:
        r = supabase_service.supabase.table('contents').select('id, title, status').order('created_at', desc=True).limit(5).execute()
        for item in r.data:
            print(f"ID: {item['id']}, Status: {item['status']}, Title: {item['title']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
