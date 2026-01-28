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
        months_since_pub = max(1, (datetime.now() - pub_date.replace(tzinfo=None)).days / 30)
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
        citation_velocity * 0.35 +
        influential_ratio * 0.25 +
        recency * 0.20 +
        author_score * 0.10 +
        category_boost * 0.10
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

def get_top_papers_by_field(papers: List[Dict[str, Any]], n_per_field: int = 1) -> List[Dict[str, Any]]:
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
                supabase.table("papers").update({"score": score}).eq("id", paper_id).execute()
    
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


def generate_selection_reason(paper: Dict[str, Any]) -> str:
    """
    Generate a human-readable reason why this paper was selected.
    Based on the scoring factors.
    """
    citations = paper.get("citationCount", 0) or 0
    influential = paper.get("influentialCitationCount", 0) or 0
    pub_date = paper.get("publicationDate") or paper.get("published_at")
    
    # Calculate metrics
    if pub_date:
        if isinstance(pub_date, str):
            try:
                pub_date = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            except:
                pub_date = datetime.now()
        days_since_pub = max(1, (datetime.now() - pub_date.replace(tzinfo=None)).days)
    else:
        days_since_pub = 30
    
    # Determine primary reason
    reasons = []
    
    # High citation velocity
    if citations > 0 and days_since_pub < 60:
        velocity = citations / (days_since_pub / 30)
        if velocity > 5:
            reasons.append(f"{citations} citations in {days_since_pub} days")
    
    # High influential ratio
    if influential > 0 and citations > 0:
        ratio = influential / citations
        if ratio > 0.3:
            reasons.append(f"{influential} influential citations")
    
    # Very recent
    if days_since_pub <= 7:
        reasons.append("published this week")
    elif days_since_pub <= 14:
        reasons.append("published in last 2 weeks")
    
    # High overall citations
    if citations >= 50:
        reasons.append(f"{citations} total citations")
    
    # Build final reason
    if reasons:
        return "Selected for: " + ", ".join(reasons[:2])
    else:
        return "Selected for: emerging research with growing interest"


def get_top_papers_with_reasons(papers: List[Dict[str, Any]], n: int = 3) -> List[Dict[str, Any]]:
    """
    Select top N papers and add selection reasons.
    """
    top = get_top_papers(papers, n)
    for paper in top:
        paper["selection_reason"] = generate_selection_reason(paper)
    return top
