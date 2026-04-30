import os
import time
import random
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from src.db import get_supabase_client

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"
SEMANTIC_FIELDS = "paperId,title,abstract,authors,citationCount,influentialCitationCount,publicationDate,url,fieldsOfStudy"
DEFAULT_REQUEST_INTERVAL_SECONDS = float(os.environ.get("SEMANTIC_SCHOLAR_REQUEST_INTERVAL_SECONDS", "2.5"))
DEFAULT_MAX_RETRIES = int(os.environ.get("SEMANTIC_SCHOLAR_MAX_RETRIES", "5"))
_last_request_at = 0.0

# STEM field mapping
FIELD_MAPPING = {
    "cs": "Computer Science",
    "physics": "Physics",
    "bio": "Biology",
    "math": "Mathematics",
}


def get_semantic_scholar_headers() -> Dict[str, str]:
    headers = {}
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key
    return headers


def wait_for_semantic_scholar_slot() -> None:
    """Keep all Semantic Scholar calls below a conservative per-process rate."""
    global _last_request_at
    now = time.monotonic()
    elapsed = now - _last_request_at
    if elapsed < DEFAULT_REQUEST_INTERVAL_SECONDS:
        time.sleep(DEFAULT_REQUEST_INTERVAL_SECONDS - elapsed)
    _last_request_at = time.monotonic()


def semantic_scholar_retry_wait(response: requests.Response, attempt: int) -> float:
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return min(float(retry_after), 180.0)
        except ValueError:
            pass

    # Semantic Scholar often omits Retry-After. Fail slowly rather than burning retries.
    base_waits = [15, 30, 60, 90, 120]
    wait = base_waits[min(attempt, len(base_waits) - 1)]
    return wait + random.uniform(0, 3)


def request_paper_search(
    query: str,
    days: int,
    limit: int,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> List[Dict[str, Any]]:
    """
    Search recent papers from Semantic Scholar with conservative throttling and 429 backoff.
    """
    url = f"{SEMANTIC_SCHOLAR_API}/paper/search"
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    params = {
        "query": query,
        "fields": SEMANTIC_FIELDS,
        "limit": limit,
        "publicationDateOrYear": f"{date_from}:",
    }
    headers = get_semantic_scholar_headers()

    for attempt in range(max_retries):
        wait_for_semantic_scholar_slot()
        response = requests.get(url, params=params, headers=headers, timeout=30)

        if response.status_code == 429:
            wait_time = semantic_scholar_retry_wait(response, attempt)
            print(
                f"Rate limited (429) for query '{query}', "
                f"waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}..."
            )
            time.sleep(wait_time)
            continue

        response.raise_for_status()
        return response.json().get("data", [])

    print(f"Failed to fetch papers for query '{query}' after {max_retries} retries")
    return []


def infer_field_from_studies(fields_of_study: Optional[List[str]]) -> Optional[str]:
    if not fields_of_study:
        return None

    normalized = {field.lower() for field in fields_of_study if field}
    if "computer science" in normalized:
        return "cs"
    if "physics" in normalized:
        return "physics"
    if "biology" in normalized or "medicine" in normalized:
        return "bio"
    if "mathematics" in normalized:
        return "math"
    return None


def fetch_papers_by_keyword(
    keyword: str, days: int = 30, limit: int = 20, max_retries: int = 3
) -> List[Dict[str, Any]]:
    """
    Search papers directly by a subscriber keyword.
    """
    cleaned = keyword.strip().lower()
    if not cleaned:
        return []

    print(f"Searching keyword '{cleaned}'...")
    papers = request_paper_search(cleaned, days=days, limit=limit, max_retries=max_retries)
    for paper in papers:
        paper.setdefault("matched_keywords", [])
        if cleaned not in paper["matched_keywords"]:
            paper["matched_keywords"].append(cleaned)
        paper["field"] = paper.get("field") or infer_field_from_studies(
            paper.get("fieldsOfStudy")
        )
    return papers


def fetch_papers_for_keywords(
    keywords: List[str], days: int = 30, limit_per_keyword: int = 20
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch keyword search results once per unique keyword for the daily run.
    """
    results = {}
    seen = []
    for keyword in keywords:
        cleaned = keyword.strip().lower()
        if cleaned and cleaned not in seen:
            seen.append(cleaned)

    for keyword in seen:
        results[keyword] = fetch_papers_by_keyword(
            keyword, days=days, limit=limit_per_keyword
        )
    return results


def fetch_papers_by_field(
    field: str, days: int = 7, limit: int = 50, max_retries: int = 3
) -> List[Dict[str, Any]]:
    """
    Fetch recent papers from Semantic Scholar API by fallback domain.
    """
    papers = request_paper_search(
        FIELD_MAPPING.get(field, field), days=days, limit=limit, max_retries=max_retries
    )

    for paper in papers:
        paper["field"] = field

    return papers


def fetch_all_fields(
    days: int = 7,
    limit_per_field: int = 50,
    fields: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch fallback papers from selected STEM domains.
    """
    all_papers = []
    target_fields = fields or list(FIELD_MAPPING.keys())

    for field in target_fields:
        if field not in FIELD_MAPPING:
            continue
        print(f"Fetching fallback {field} papers...")
        all_papers.extend(fetch_papers_by_field(field, days, limit_per_field))
        time.sleep(1)

    return all_papers


def save_papers_to_db(papers: List[Dict[str, Any]]) -> int:
    """
    Save papers to Supabase (with duplicate check)
    """
    supabase = get_supabase_client()
    saved_count = 0

    for paper in papers:
        paper_data = {
            "source": "semantic_scholar",
            "external_id": paper.get("paperId"),
            "title": paper.get("title"),
            "authors": [a.get("name") for a in paper.get("authors", [])],
            "abstract": paper.get("abstract"),
            "url": paper.get("url"),
            "published_at": paper.get("publicationDate"),
        }

        try:
            supabase.table("papers").upsert(
                paper_data, on_conflict="source,external_id"
            ).execute()
            saved_count += 1
        except Exception as e:
            print(f"Error saving paper: {e}")

    return saved_count


def main():
    """
    Main: Fetch papers and save to DB
    """
    print("Fetching papers from Semantic Scholar...")
    papers = fetch_all_fields(days=7, limit_per_field=50)
    print(f"Fetched {len(papers)} papers total")

    print("Saving to database...")
    saved = save_papers_to_db(papers)
    print(f"Saved {saved} papers to database")


if __name__ == "__main__":
    main()
