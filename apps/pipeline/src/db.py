import os
from datetime import datetime, timedelta
from typing import List

from supabase import create_client, Client


def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
    return create_client(url, key)


def get_recently_sent_paper_ids(subscriber_email: str, days: int = 7) -> List[str]:
    supabase = get_supabase_client()
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    try:
        result = (
            supabase.table("sent_papers")
            .select("paper_id")
            .eq("subscriber_email", subscriber_email)
            .gte("sent_at", cutoff)
            .execute()
        )
        return [row["paper_id"] for row in (result.data or [])]
    except Exception:
        return []


def save_sent_papers(paper_ids: List[str], subscriber_email: str) -> None:
    supabase = get_supabase_client()
    rows = [
        {"paper_id": pid, "subscriber_email": subscriber_email} for pid in paper_ids
    ]
    try:
        supabase.table("sent_papers").insert(rows).execute()
    except Exception as e:
        print(f"Error saving sent papers: {e}")
