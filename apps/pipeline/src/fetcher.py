import os
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from src.db import get_supabase_client

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"

# STEM 분야 매핑
FIELD_MAPPING = {
    "cs": "Computer Science",
    "physics": "Physics",
    "bio": "Biology",
    "math": "Mathematics"
}


def fetch_papers_by_field(field: str, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Semantic Scholar API로 특정 분야의 최근 논문 수집
    Rate limit: 1 request per second
    """
    url = f"{SEMANTIC_SCHOLAR_API}/paper/search"

    # 최근 N일 논문
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    params = {
        "query": FIELD_MAPPING.get(field, field),
        "fields": "paperId,title,abstract,authors,citationCount,influentialCitationCount,publicationDate,url,fieldsOfStudy",
        "limit": limit,
        "publicationDateOrYear": f"{date_from}:",
    }

    headers = {}
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    data = response.json()
    return data.get("data", [])


def fetch_all_fields(days: int = 7, limit_per_field: int = 50) -> List[Dict[str, Any]]:
    """
    모든 STEM 분야에서 논문 수집
    """
    all_papers = []

    for field in FIELD_MAPPING.keys():
        print(f"Fetching {field} papers...")
        papers = fetch_papers_by_field(field, days, limit_per_field)

        for paper in papers:
            paper["field"] = field

        all_papers.extend(papers)
        time.sleep(1)  # Rate limiting: 1 RPS

    return all_papers


def save_papers_to_db(papers: List[Dict[str, Any]]) -> int:
    """
    논문을 Supabase에 저장 (중복 체크)
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

        # Upsert (중복이면 무시)
        try:
            supabase.table("papers").upsert(
                paper_data,
                on_conflict="source,external_id"
            ).execute()
            saved_count += 1
        except Exception as e:
            print(f"Error saving paper: {e}")

    return saved_count


def main():
    """
    메인 실행: 논문 수집 + DB 저장
    """
    print("Fetching papers from Semantic Scholar...")
    papers = fetch_all_fields(days=7, limit_per_field=50)
    print(f"Fetched {len(papers)} papers total")

    print("Saving to database...")
    saved = save_papers_to_db(papers)
    print(f"Saved {saved} papers to database")


if __name__ == "__main__":
    main()
