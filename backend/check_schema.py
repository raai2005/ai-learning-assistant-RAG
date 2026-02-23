import asyncio
from app.services import supabase_service

async def main():
    try:
        r = supabase_service.supabase.table('contents').select('*').limit(1).execute()
        if r.data:
            print("COLUMNS:")
            for k in r.data[0].keys():
                print(f" - {k}")
        else:
            print("No data found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
