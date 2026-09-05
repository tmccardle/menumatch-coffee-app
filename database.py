import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

# Load .env from the same folder as this file (the FastAPI project root).
load_dotenv(Path(__file__).resolve().parent / ".env")

url = os.environ.get("SUPABASE_URL")
key = (
    os.environ.get("SUPABASE_ANON_KEY")
    or os.environ.get("SUPABASE_KEY")
    or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
)

if not url or not key:
    raise RuntimeError(
        "Missing Supabase settings. Put SUPABASE_URL and SUPABASE_ANON_KEY in .env "
        "next to app.py. Do not commit .env."
    )

supabase = create_client(url, key)
