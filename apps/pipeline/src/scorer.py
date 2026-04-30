from datetime import datetime
from typing import List, Dict, Any, Optional
from src.db import get_supabase_client


DIGEST_CATEGORIES = [
    "New in your field",
    "Heating up",
    "Adjacent Insight",
]


def calculate_score(paper: Dict[str, Any]) -> float:
    """
    Calculate paper score

    Score = citation_velocity * 0.35 +
            influential_ratio * 0.25 +
            recency * 0.20 +
            author_score * 0.10 +
            category_boost * 0.10
    """
    # Citation velocity (citations per month)
    citations = paper.get("citationCount", 0) or 0
    pub_date = paper.get("publicationDate") or paper.get("published_at")

    if pub_date:
        if isinstance(pub_date, str):
            try:
                pub_date = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            except:
                pub_date = datetime.now()
        months_since_pub = max(
            1, (datetime.now() - pub_date.replace(tzinfo=None)).days / 30
        )
    else:
        months_since_pub = 1

    citation_velocity = citations / months_since_pub

    # Influential citation ratio
    influential = paper.get("influentialCitationCount", 0) or 0
    influential_ratio = influential / max(1, citations)

    # Recency factor (newer = higher)
    recency = 1 / (1 + months_since_pub / 6)  # Decay over 6 months

    # Author score (simplified - just use citation count as proxy)
    author_score = min(1.0, citations / 100)  # Cap at 100 citations

    # Category boost (all equal for now)
    category_boost = 0.5

    # Final score
    score = (
        citation_velocity * 0.35
        + influential_ratio * 0.25
        + recency * 0.20
        + author_score * 0.10
        + category_boost * 0.10
    )

    return round(score, 4)


def score_papers(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Calculate scores for all papers and sort
    """
    for paper in papers:
        paper["score"] = calculate_score(paper)

    return sorted(papers, key=lambda x: x["score"], reverse=True)


def get_top_papers(papers: List[Dict[str, Any]], n: int = 3) -> List[Dict[str, Any]]:
    """
    Select top N papers
    """
    scored = score_papers(papers)
    return scored[:n]


def get_top_papers_by_field(
    papers: List[Dict[str, Any]], n_per_field: int = 1
) -> List[Dict[str, Any]]:
    """
    Select top N papers per field
    """
    # Group by field
    by_field = {}
    for paper in papers:
        field = paper.get("field", "unknown")
        if field not in by_field:
            by_field[field] = []
        by_field[field].append(paper)

    # Get top N from each field
    top_papers = []
    for field, field_papers in by_field.items():
        scored = score_papers(field_papers)
        top_papers.extend(scored[:n_per_field])

    # Sort all by score
    return sorted(top_papers, key=lambda x: x["score"], reverse=True)


def update_paper_scores_in_db():
    """
    Update scores for papers in DB
    """
    supabase = get_supabase_client()

    # Get all papers
    result = supabase.table("papers").select("*").execute()
    papers = result.data if result.data else []

    # Calculate and update scores
    for paper in papers:
        if isinstance(paper, dict):
            score = calculate_score(paper)
            paper_id = paper.get("id")
            if paper_id:
                supabase.table("papers").update({"score": score}).eq(
                    "id", paper_id
                ).execute()

    print(f"Updated scores for {len(papers)} papers")


def main():
    """
    Test run
    """
    # Example paper
    test_paper = {
        "title": "Test Paper",
        "citationCount": 50,
        "influentialCitationCount": 10,
        "publicationDate": "2026-01-15",
    }

    score = calculate_score(test_paper)
    print(f"Test paper score: {score}")


if __name__ == "__main__":
    main()


def normalize_keywords(keywords: List[str], limit: int = 3) -> List[str]:
    normalized = []
    for keyword in keywords or []:
        cleaned = str(keyword).strip().lower()
        if cleaned and cleaned not in normalized:
            normalized.append(cleaned)
        if len(normalized) == limit:
            break
    return normalized


def get_search_text(paper: Dict[str, Any]) -> str:
    fields = paper.get("fieldsOfStudy") or []
    return " ".join(
        [
            str(paper.get("title") or ""),
            str(paper.get("abstract") or ""),
            " ".join(str(field) for field in fields),
        ]
    ).lower()


def get_keyword_match_details(
    paper: Dict[str, Any], keywords: List[str]
) -> Dict[str, Any]:
    title = str(paper.get("title") or "").lower()
    abstract = str(paper.get("abstract") or "").lower()
    fields = " ".join(str(field) for field in paper.get("fieldsOfStudy") or []).lower()

    matches = []
    score = 0.0
    for keyword in normalize_keywords(keywords):
        location = None
        if keyword in title:
            location = "title"
            score += 5.0
        elif keyword in abstract:
            location = "abstract"
            score += 2.0
        elif keyword in fields:
            location = "field metadata"
            score += 1.0
        elif keyword in paper.get("matched_keywords", []):
            location = "search result"
            score += 0.5

        if location:
            matches.append({"keyword": keyword, "location": location})

    return {"matches": matches, "score": score}


def parse_publication_date(paper: Dict[str, Any]) -> Optional[datetime]:
    pub_date = paper.get("publicationDate") or paper.get("published_at")
    if not pub_date:
        return None
    if isinstance(pub_date, datetime):
        return pub_date.replace(tzinfo=None)
    try:
        return datetime.fromisoformat(str(pub_date).replace("Z", "+00:00")).replace(
            tzinfo=None
        )
    except (TypeError, ValueError):
        return None


def days_since_publication(paper: Dict[str, Any]) -> Optional[int]:
    pub_date = parse_publication_date(paper)
    if not pub_date:
        return None
    return max(0, (datetime.now() - pub_date).days)


def is_recent_paper(paper: Dict[str, Any], days: int) -> bool:
    age = days_since_publication(paper)
    return age is not None and age <= days


def citation_velocity_score(paper: Dict[str, Any]) -> float:
    citations = paper.get("citationCount", 0) or 0
    age = days_since_publication(paper)
    months_since_pub = max(1.0, (age if age is not None else 30) / 30)
    citations_per_month = citations / months_since_pub
    return min(1.0, citations_per_month / 10)


def influential_score(paper: Dict[str, Any]) -> float:
    influential = paper.get("influentialCitationCount", 0) or 0
    return min(1.0, influential / 10)


def total_citations_score(paper: Dict[str, Any]) -> float:
    citations = paper.get("citationCount", 0) or 0
    return min(1.0, citations / 100)


def recency_score(paper: Dict[str, Any], window_days: int) -> float:
    age = days_since_publication(paper)
    if age is None or age > window_days:
        return 0.0
    return max(0.0, (window_days - age) / window_days)


def keyword_score(match_details: Dict[str, Any]) -> float:
    return min(1.0, (match_details.get("score", 0.0) or 0.0) / 5.0)


def paper_in_preferred_fields(
    paper: Dict[str, Any], preferred_fields: List[str]
) -> bool:
    if not preferred_fields:
        return True
    return paper.get("field") in preferred_fields


def paper_is_adjacent(
    paper: Dict[str, Any], preferred_fields: List[str]
) -> bool:
    field = paper.get("field")
    if field in (None, "", "other", "unknown"):
        return True
    return bool(preferred_fields) and field not in preferred_fields


def score_digest_category(
    paper: Dict[str, Any], category: str, match_details: Dict[str, Any]
) -> float:
    if category == "New in your field":
        return (
            influential_score(paper) * 40
            + citation_velocity_score(paper) * 50
            + recency_score(paper, 30) * 10
        )
    if category == "Heating up":
        return (
            citation_velocity_score(paper) * 60
            + influential_score(paper) * 25
            + total_citations_score(paper) * 15
        )
    if category == "Adjacent Insight":
        return (
            keyword_score(match_details) * 40
            + citation_velocity_score(paper) * 30
            + influential_score(paper) * 20
            + recency_score(paper, 180) * 10
        )
    return paper.get("score", 0)


def category_candidate_papers(
    papers: List[Dict[str, Any]],
    category: str,
    preferred_fields: List[str],
    keywords: List[str],
    unavailable_ids: set,
) -> List[Dict[str, Any]]:
    candidates = []
    for paper in papers:
        paper_id = paper.get("paperId") or paper.get("external_id") or paper.get("url")
        if not paper_id or paper_id in unavailable_ids:
            continue

        match_details = get_keyword_match_details(paper, keywords) if keywords else {
            "matches": [],
            "score": 0.0,
        }
        if keywords and not match_details["matches"]:
            continue

        if category == "New in your field":
            if not is_recent_paper(paper, 30) or not paper_in_preferred_fields(
                paper, preferred_fields
            ):
                continue
        elif category == "Heating up":
            if not is_recent_paper(paper, 90) or not paper_in_preferred_fields(
                paper, preferred_fields
            ):
                continue
        elif category == "Adjacent Insight":
            if (
                not is_recent_paper(paper, 180)
                or not match_details["matches"]
                or not paper_is_adjacent(paper, preferred_fields)
            ):
                continue

        candidate = {**paper}
        candidate["keyword_matches"] = match_details["matches"]
        candidate["category"] = category
        candidate["selection_category"] = category
        candidate["personalized_score"] = round(
            score_digest_category(candidate, category, match_details), 4
        )
        candidates.append(candidate)

    return sorted(
        candidates,
        key=lambda paper: paper.get("personalized_score", paper.get("score", 0)),
        reverse=True,
    )


def dedupe_papers(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    deduped = []
    for paper in papers:
        paper_id = paper.get("paperId") or paper.get("external_id") or paper.get("url")
        if not paper_id or paper_id in seen:
            continue
        seen.add(paper_id)
        deduped.append(paper)
    return deduped


def filter_papers_by_fields(
    papers: List[Dict[str, Any]], fields: List[str]
) -> List[Dict[str, Any]]:
    """
    Filter papers by preferred fallback domains.
    If fields is empty or None, return all papers.
    """
    if not fields:
        return papers

    return [p for p in papers if p.get("field") in fields]


def generate_selection_reason(paper: Dict[str, Any]) -> str:
    """
    Generate a human-readable reason why this paper was selected.
    Keyword matches are reported before general quality signals.
    """
    keyword_matches = paper.get("keyword_matches") or []
    if keyword_matches:
        first = keyword_matches[0]
        keyword = first.get("keyword")
        location = first.get("location")
        category = paper.get("category")
        prefix = f"{category}: " if category else ""
        return f'{prefix}matches your keyword "{keyword}" in {location}'

    citations = paper.get("citationCount", 0) or 0
    influential = paper.get("influentialCitationCount", 0) or 0
    pub_date = paper.get("publicationDate") or paper.get("published_at")

    if pub_date:
        if isinstance(pub_date, str):
            try:
                pub_date = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            except:
                pub_date = datetime.now()
        days_since_pub = max(1, (datetime.now() - pub_date.replace(tzinfo=None)).days)
    else:
        days_since_pub = 30

    reasons = []
    if citations > 0 and days_since_pub < 60:
        velocity = citations / (days_since_pub / 30)
        if velocity > 5:
            reasons.append(f"{citations} citations in {days_since_pub} days")

    if influential > 0 and citations > 0:
        ratio = influential / citations
        if ratio > 0.3:
            reasons.append(f"{influential} influential citations")

    if days_since_pub <= 7:
        reasons.append("published this week")
    elif days_since_pub <= 14:
        reasons.append("published in last 2 weeks")

    if citations >= 50:
        reasons.append(f"{citations} total citations")

    if reasons:
        reason = ", ".join(reasons[:2])
    else:
        reason = "emerging research with growing interest"

    category = paper.get("category")
    return f"{category}: {reason}" if category else f"Selected for: {reason}"


def get_top_papers_with_reasons(
    papers: List[Dict[str, Any]], n: int = 3
) -> List[Dict[str, Any]]:
    top = get_top_papers(papers, n)
    for paper in top:
        paper["selection_reason"] = generate_selection_reason(paper)
    return top


def select_personalized_papers(
    keyword_papers: List[Dict[str, Any]],
    fallback_papers: List[Dict[str, Any]],
    preferred_fields: List[str],
    preferred_keywords: List[str],
    sent_ids: List[str],
    n: int = 3,
) -> List[Dict[str, Any]]:
    """
    Select a subscriber digest with at most one paper from each digest category:
    New in your field, Heating up, and Adjacent Insight.
    """
    sent = set(sent_ids or [])
    keywords = normalize_keywords(preferred_keywords)
    all_candidates = dedupe_papers(keyword_papers + fallback_papers)
    selected = []
    unavailable_ids = set(sent)

    for category in DIGEST_CATEGORIES[:n]:
        candidates = category_candidate_papers(
            all_candidates, category, preferred_fields, keywords, unavailable_ids
        )
        if not candidates:
            continue
        chosen = candidates[0]
        selected.append(chosen)
        paper_id = chosen.get("paperId") or chosen.get("external_id") or chosen.get("url")
        if paper_id:
            unavailable_ids.add(paper_id)

    for paper in selected:
        paper["selection_reason"] = generate_selection_reason(paper)

    return selected


# Backward-compatible wrapper for older callers/tests.
def get_personalized_papers(
    all_papers: List[Dict[str, Any]], preferred_fields: List[str], n: int = 3
) -> List[Dict[str, Any]]:
    filtered = filter_papers_by_fields(all_papers, preferred_fields)
    return sorted(filtered, key=lambda x: x.get("score", 0), reverse=True)[:n]
