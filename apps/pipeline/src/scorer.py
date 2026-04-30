from datetime import datetime
from typing import List, Dict, Any
from src.db import get_supabase_client


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
        return f'Selected for: matches your keyword "{keyword}" in {location}'

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
        return "Selected for: " + ", ".join(reasons[:2])
    return "Selected for: emerging research with growing interest"


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
    Select a subscriber digest: keyword search results first, then selected-domain fallback.
    """
    sent = set(sent_ids or [])
    keywords = normalize_keywords(preferred_keywords)

    keyword_candidates = []
    if keywords:
        for paper in dedupe_papers(keyword_papers):
            if paper.get("paperId") in sent:
                continue
            match_details = get_keyword_match_details(paper, keywords)
            if not match_details["matches"]:
                continue
            candidate = {**paper}
            candidate["keyword_matches"] = match_details["matches"]
            candidate["personalized_score"] = candidate.get("score", 0) + match_details["score"]
            keyword_candidates.append(candidate)

    keyword_candidates = sorted(
        keyword_candidates,
        key=lambda paper: paper.get("personalized_score", paper.get("score", 0)),
        reverse=True,
    )

    selected = keyword_candidates[:n]
    selected_ids = {paper.get("paperId") for paper in selected}

    if len(selected) < n:
        fallback_candidates = []
        for paper in filter_papers_by_fields(dedupe_papers(fallback_papers), preferred_fields):
            paper_id = paper.get("paperId")
            if paper_id in sent or paper_id in selected_ids:
                continue
            fallback_candidates.append(paper)

        fallback_candidates = sorted(
            fallback_candidates, key=lambda paper: paper.get("score", 0), reverse=True
        )
        selected.extend(fallback_candidates[: n - len(selected)])

    for paper in selected:
        paper["selection_reason"] = generate_selection_reason(paper)

    return selected[:n]


# Backward-compatible wrapper for older callers/tests.
def get_personalized_papers(
    all_papers: List[Dict[str, Any]], preferred_fields: List[str], n: int = 3
) -> List[Dict[str, Any]]:
    filtered = filter_papers_by_fields(all_papers, preferred_fields)
    return sorted(filtered, key=lambda x: x.get("score", 0), reverse=True)[:n]
