import os
from typing import List, Dict, Any
from groq import Groq

def get_groq_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY must be set")
    return Groq(api_key=api_key)

def summarize_paper(paper: Dict[str, Any]) -> str:
    """
    Generate a concise 1-2 sentence paper summary using Groq.
    No emojis, no formatting - just plain text.
    """
    client = get_groq_client()
    
    title = paper.get("title", "Unknown")
    abstract = paper.get("abstract", "No abstract available")
    
    prompt = f"""Summarize this paper in 1-2 sentences. Be concise and technical.
Focus on: What did they do? Why does it matter?
Target audience: researchers who want a quick morning read.

Title: {title}
Abstract: {abstract}

Write only the summary, no headers or formatting."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.3,
    )
    
    return response.choices[0].message.content

def summarize_papers(papers: List[Dict[str, Any]], max_papers: int = 3) -> List[Dict[str, Any]]:
    """
    Summarize multiple papers (default: top 3)
    """
    summaries = []
    
    for paper in papers[:max_papers]:
        try:
            summary = summarize_paper(paper)
            summaries.append({
                **paper,
                "summary": summary
            })
            print(f"Summarized: {paper.get('title', 'Unknown')[:50]}...")
        except Exception as e:
            print(f"Error summarizing paper: {e}")
            summaries.append({
                **paper,
                "summary": f"Summary unavailable: {str(e)}"
            })
    
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
    """
    Test run
    """
    test_paper = {
        "title": "Scaling Test-Time Compute Optimally",
        "abstract": "We study how to optimally scale test-time compute in language models. We find that allowing models to 'think longer' by generating more tokens before answering can significantly improve performance. Our process reward model approach achieves 14x better compute efficiency compared to simply using larger models.",
        "url": "https://arxiv.org/abs/example"
    }
    
    print("Testing summarizer...")
    summary = summarize_paper(test_paper)
    print(summary)

if __name__ == "__main__":
    main()
