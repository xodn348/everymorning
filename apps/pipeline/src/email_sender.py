import os
import html
from typing import List, Dict, Any
import resend


def get_resend_client():
    """Initialize Resend client."""
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise ValueError("RESEND_API_KEY must be set")
    resend.api_key = api_key
    return resend


def format_email_html(papers: List[Dict[str, Any]]) -> str:
    """Format papers into HTML email."""
    email_html = """
    <html>
    <head>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f9fafb; }
            .header { text-align: center; padding: 20px 0; }
            .header h1 { color: #111827; margin: 0; }
            .paper { background: white; border-radius: 8px; padding: 20px; margin: 16px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
            .paper h2 { color: #1f2937; margin: 0 0 12px 0; font-size: 18px; }
            .summary { color: #374151; line-height: 1.6; white-space: pre-wrap; }
            .link { display: inline-block; margin-top: 12px; color: #3b82f6; text-decoration: none; }
            .footer { text-align: center; color: #6b7280; font-size: 12px; padding: 20px 0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📚 everymorning</h1>
            <p>Daily STEM Paper Digest</p>
        </div>
    """
    
    for i, paper in enumerate(papers, 1):
        title = html.escape(paper.get("title", "Unknown"))
        summary = html.escape(paper.get("summary", "No summary available"))
        url = paper.get("url", "")
        
        link_html = f"<a class='link' href='{url}'>Read paper →</a>" if url else ""
        
        email_html += f"""
        <div class="paper">
            <h2>#{i} {title}</h2>
            <div class="summary">{summary}</div>
            {link_html}
        </div>
        """
    
    email_html += """
        <div class="footer">
            <p>You received this because you subscribed to everymorning.</p>
        </div>
    </body>
    </html>
    """
    return email_html


def send_digest_email(
    to_emails: List[str], 
    papers: List[Dict[str, Any]], 
    from_email: str = None
) -> Dict[str, Any]:
    """Send digest email to subscribers."""
    get_resend_client()
    
    if from_email is None:
        from_email = os.environ.get("RESEND_FROM_EMAIL", "onboarding@resend.dev")
    
    html_content = format_email_html(papers)
    
    results = []
    for email in to_emails:
        try:
            result = resend.Emails.send({
                "from": from_email,
                "to": email,
                "subject": "📚 everymorning - Today's Top STEM Papers",
                "html": html_content
            })
            results.append({"email": email, "status": "sent", "id": result.get("id")})
            print(f"Email sent to {email}")
        except Exception as e:
            results.append({"email": email, "status": "failed", "error": str(e)})
            print(f"Failed to send to {email}: {e}")
    
    return {
        "results": results, 
        "total": len(to_emails), 
        "sent": sum(1 for r in results if r["status"] == "sent")
    }


def main():
    """Test run - generates HTML preview."""
    test_papers = [{
        "title": "Test Paper",
        "summary": "Test summary content",
        "url": "https://example.com"
    }]
    
    email_html = format_email_html(test_papers)
    print("HTML Preview generated successfully")
    print(f"Length: {len(email_html)} characters")


if __name__ == "__main__":
    main()
