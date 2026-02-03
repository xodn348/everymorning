import os
from typing import List, Dict, Any
from groq import Groq

# Input length limits to prevent prompt injection
MAX_TITLE_LENGTH = 300
MAX_ABSTRACT_LENGTH = 3000


def get_groq_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY must be set")
    return Groq(api_key=api_key)


def sanitize_input(text: str, max_length: int) -> str:
    """Sanitize and truncate input text."""
    if not text:
        return ""
    # Remove potential control characters and truncate
    cleaned = "".join(char for char in text if char.isprintable() or char in "\n\t")
    return cleaned[:max_length]


def summarize_paper(paper: Dict[str, Any]) -> str:
    """
    Generate a concise 3-point bullet summary using Groq.
    Returns bullet points for better readability.
    """
    client = get_groq_client()

    # Sanitize inputs to prevent prompt injection
    title = sanitize_input(paper.get("title", "Unknown"), MAX_TITLE_LENGTH)
    abstract = sanitize_input(
        paper.get("abstract", "No abstract available"), MAX_ABSTRACT_LENGTH
    )

    prompt = f"""Summarize this paper in exactly 3 short bullet points.
Each point should be ONE sentence maximum.
Use this format:
• [What they did/key method]
• [Main finding/result]
• [Why it matters/impact]

Target audience: researchers scanning papers over morning coffee.

Title: {title}
Abstract: {abstract}

Write ONLY the 3 bullet points, nothing else."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.3,
    )

    return (
        response.choices[0].message.content
        or "• Summary unavailable\n• Please check paper directly\n• Error generating summary"
    )


def summarize_papers(
    papers: List[Dict[str, Any]], max_papers: int = 3
) -> List[Dict[str, Any]]:
    """
    Summarize multiple papers (default: top 3)
    """
    summaries = []

    for paper in papers[:max_papers]:
        try:
            summary = summarize_paper(paper)
            summaries.append({**paper, "summary": summary})
            # Don't log full title for privacy
            print(f"Summarized paper {len(summaries)}/{max_papers}")
        except Exception as e:
            # Don't expose error details in output
            print(f"Error summarizing paper {len(summaries) + 1}")
            summaries.append({**paper, "summary": "Summary temporarily unavailable"})

    return summaries


def format_digest(papers: List[Dict[str, Any]]) -> str:
    """
    Format into digest for email/telegram
    """
    lines = ["everymorning - Daily STEM Paper Digest\n"]
    lines.append("=" * 40 + "\n")

    for i, paper in enumerate(papers, 1):
        title = paper.get("title", "Unknown")
        url = paper.get("url", "")
        summary = paper.get("summary", "No summary")

        lines.append(f"\nPaper #{i}: {title}\n")
        lines.append("-" * 40)
        lines.append(f"\n{summary}\n")
        if url:
            lines.append(f"\nRead paper: {url}\n")
        lines.append("\n" + "=" * 40)

    return "\n".join(lines)


def main():
    """Test run"""
    test_paper = {
        "title": "Scaling Test-Time Compute Optimally",
        "abstract": "We study how to optimally scale test-time compute in language models.",
        "url": "https://arxiv.org/abs/example",
    }

    print("Testing summarizer...")
    summary = summarize_paper(test_paper)
    print(summary)


if __name__ == "__main__":
    main()
