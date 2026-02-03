import os
import html
from typing import List, Dict, Any
from urllib.parse import quote
import resend


def get_resend_client():
    """Initialize Resend client."""
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise ValueError("RESEND_API_KEY must be set")
    resend.api_key = api_key
    return resend


def mask_email(email: str) -> str:
    """Mask email for logging (show first 3 chars and domain)."""
    if "@" in email:
        local, domain = email.split("@", 1)
        masked_local = local[:3] + "***" if len(local) > 3 else "***"
        return f"{masked_local}@{domain}"
    return "***"


def format_email_html(papers: List[Dict[str, Any]]) -> str:
    """Format papers into minimal HTML email with proper escaping."""
    
    papers_html = ""
    for paper in papers:
        title = html.escape(paper.get("title", "Unknown"))
        summary = html.escape(paper.get("summary", "No summary available"))
        selection_reason = html.escape(paper.get("selection_reason", ""))
        # Escape URL to prevent injection
        raw_url = paper.get("url", "#")
        url = html.escape(raw_url) if raw_url else "#"
        
        papers_html += f'''
          <tr>
            <td style="padding: 20px; background: #ffffff; border-radius: 8px;">
              <a href="{url}" style="text-decoration: none;">
                <h2 style="margin: 0 0 8px 0; font-size: 15px; font-weight: 600; color: #111827; line-height: 1.4;">
                  {title}
                </h2>
              </a>
              <p style="margin: 0 0 8px 0; font-size: 12px; color: #0891b2; font-weight: 500;">
                  {selection_reason}
                </p>
              <p style="margin: 0; font-size: 14px; color: #4b5563; line-height: 1.5;">
                {summary}
              </p>
            </td>
          </tr>
          <tr><td style="height: 12px;"></td></tr>
        '''
    
    email_html = f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light dark">
</head>
<body style="margin: 0; padding: 0; background-color: #f9fafb; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding: 40px 20px;">
    <tr>
      <td align="center">
        <table width="520" cellpadding="0" cellspacing="0" style="max-width: 520px; width: 100%;">
          
          <tr>
            <td style="padding-bottom: 32px;">
              <h1 style="margin: 0; font-size: 20px; font-weight: 600; color: #111827;">
                everymorning
              </h1>
              <p style="margin: 4px 0 0 0; font-size: 13px; color: #6b7280;">
                Daily STEM Paper Digest
              </p>
            </td>
          </tr>
          
          {papers_html}
          
          <tr>
            <td style="padding-top: 32px; border-top: 1px solid #e5e7eb;">
              <p style="margin: 0; font-size: 12px; color: #9ca3af; text-align: center;">
                Unsubscribe
              </p>
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>
</body>
</html>'''
    return email_html


def send_digest_email(
    to_emails: List[str], 
    papers: List[Dict[str, Any]], 
    from_email: str = None
) -> Dict[str, Any]:
    """Send digest email to subscribers."""
    get_resend_client()
    
    if from_email is None:
        from_email = os.environ.get("RESEND_FROM_EMAIL", "everymorning <newsletter@stemem.info>")
    
    html_content = format_email_html(papers)
    
    results = []
    for email in to_emails:
        masked = mask_email(email)
        try:
            result = resend.Emails.send({
                "from": from_email,
                "to": email,
                "subject": "everymorning - Today's Top STEM Papers",
                "html": html_content
            })
            results.append({"email": email, "status": "sent", "id": result.get("id")})
            print(f"Email sent to {masked}")
        except Exception as e:
            results.append({"email": email, "status": "failed", "error": "Send error"})
            print(f"Failed to send to {masked}")
    
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
