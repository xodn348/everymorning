import os
import html
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import resend


FIELD_MAPPING = {
    "cs": "Computer Science",
    "physics": "Physics",
    "bio": "Biology",
    "math": "Mathematics",
}


def generate_ai_prompt(title: str, field: str, summary: str) -> str:
    truncated_title = title[:120] if len(title) > 120 else title
    field_name = FIELD_MAPPING.get(field, field)

    prompt = f"""I'd like your help analyzing this research paper.

Title: {truncated_title}
Field: {field_name}
Summary: {summary}

Please:
1. Summarize the key contributions and methodology
2. Identify how this connects to my research in [YOUR RESEARCH TOPIC]
3. Suggest 2-3 novel research directions combining these ideas
4. Note any limitations or open questions worth exploring"""

    return prompt


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


def format_email_html(
    papers: List[Dict[str, Any]], recipient_email: Optional[str] = None
) -> str:
    papers_html = ""
    for paper in papers:
        title = html.escape(paper.get("title", "Unknown"))
        summary = html.escape(paper.get("summary", "No summary available"))
        selection_reason = html.escape(paper.get("selection_reason", ""))
        raw_url = paper.get("url", "#")
        url = html.escape(raw_url) if raw_url else "#"
        field = paper.get("field", "")

        ai_prompt = generate_ai_prompt(
            paper.get("title", ""), field, paper.get("summary", "")
        )
        escaped_prompt = html.escape(ai_prompt)

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
              <p style="margin: 12px 0 8px 0; font-size: 11px; color: #6b7280;">
                AI Prompt
              </p>
              <pre style="margin: 0; background: #f3f4f6; padding: 12px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 12px; color: #374151; white-space: pre-wrap; word-wrap: break-word; overflow-x: auto;">{escaped_prompt}</pre>
            </td>
          </tr>
          <tr><td style="height: 12px;"></td></tr>
        '''

    unsubscribe_link = ""
    if recipient_email:
        encoded_email = quote(recipient_email)
        unsubscribe_link = f'<a href="https://stemem.info/unsubscribe?email={encoded_email}" style="color: #0891b2; text-decoration: none;">Unsubscribe</a>'
    else:
        unsubscribe_link = "Unsubscribe"

    email_html = f"""<!DOCTYPE html>
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
                {unsubscribe_link}
              </p>
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    return email_html


def send_digest_email(
    to_emails: List[str],
    papers: List[Dict[str, Any]],
    from_email: Optional[str] = None,
    recipient_email: Optional[str] = None,
) -> Dict[str, Any]:
    """Send digest email to subscribers."""
    get_resend_client()

    if from_email is None:
        from_email = os.environ.get(
            "RESEND_FROM_EMAIL", "everymorning <fresh@stemem.info>"
        )

    results = []
    for email in to_emails:
        masked = mask_email(email)
        html_content = format_email_html(papers, recipient_email=email)
        try:
            result = resend.Emails.send(
                {
                    "from": from_email,
                    "to": email,
                    "subject": "everymorning - Today's Top STEM Papers",
                    "html": html_content,
                }
            )
            results.append({"email": email, "status": "sent", "id": result.get("id")})
            print(f"Email sent to {masked}")
        except Exception as e:
            results.append({"email": email, "status": "failed", "error": "Send error"})
            print(f"Failed to send to {masked}")

    return {
        "results": results,
        "total": len(to_emails),
        "sent": sum(1 for r in results if r["status"] == "sent"),
    }


def main():
    test_papers = [
        {
            "title": "Test Paper",
            "summary": "Test summary content",
            "url": "https://example.com",
            "field": "cs",
            "selection_reason": "Relevant to your interests",
        }
    ]

    email_html = format_email_html(test_papers, recipient_email="test@example.com")
    print("HTML Preview generated successfully")
    print(f"Length: {len(email_html)} characters")


if __name__ == "__main__":
    main()
