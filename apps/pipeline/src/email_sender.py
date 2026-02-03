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


def generate_ai_prompt(title: str, field: str, summary: str, url: str = "") -> str:
    truncated_title = title[:100] if len(title) > 100 else title
    field_name = FIELD_MAPPING.get(field, field)
    truncated_summary = summary[:200] if len(summary) > 200 else summary

    url_part = f" ({url})" if url else ""

    prompt = f"""Paper: {truncated_title}{url_part}
Field: {field_name}
Summary: {truncated_summary}

Analyze key findings, how they connect to my research in [YOUR TOPIC], and suggest novel research directions."""

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


def convert_bullets_to_html(text: str) -> str:
    lines = text.strip().split("\n")
    bullets = []
    for line in lines:
        line = line.strip()
        if line.startswith("•"):
            bullets.append(line[1:].strip())
        elif line.startswith("-"):
            bullets.append(line[1:].strip())
        elif line:
            bullets.append(line)

    if bullets:
        items_html = "".join(
            f'<li style="margin-bottom: 8px; text-align: left;">{html.escape(item)}</li>'
            for item in bullets
        )
        return f'<ul style="margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;">{items_html}</ul>'
    return html.escape(text)


def format_email_html(
    papers: List[Dict[str, Any]], recipient_email: Optional[str] = None
) -> str:
    papers_html = ""
    for idx, paper in enumerate(papers, 1):
        title = html.escape(paper.get("title", "Unknown"))
        raw_summary = paper.get("summary", "No summary available")
        summary_html = convert_bullets_to_html(raw_summary)
        selection_reason = html.escape(paper.get("selection_reason", ""))
        raw_url = paper.get("url", "#")
        url = html.escape(raw_url) if raw_url else "#"
        field = paper.get("field", "")

        paper_number = f"0{idx}" if idx < 10 else str(idx)

        ai_prompt = generate_ai_prompt(
            paper.get("title", ""),
            field,
            paper.get("summary", ""),
            paper.get("url", ""),
        )
        escaped_prompt = html.escape(ai_prompt)

        papers_html += f'''
          <tr>
            <td style="padding: 0 0 20px 0;">
              <table width="100%" cellpadding="0" cellspacing="0" style="background: #f9f9fb; border: 1px solid #e2e2e8; border-radius: 8px;">
                <tr>
                  <td style="padding: 24px; text-align: left;">
                    <div style="margin-bottom: 12px; text-align: left;">
                      <span style="display: inline-block; padding: 4px 10px; background: #6366f1; color: #ffffff; font-size: 12px; font-weight: 600; border-radius: 4px;">{paper_number}</span>
                    </div>
                    <a href="{url}" style="text-decoration: none;">
                      <h2 style="margin: 0 0 10px 0; font-size: 17px; font-weight: 600; color: #111827; line-height: 1.5; text-align: left;">
                        {title}
                      </h2>
                    </a>
                    <p style="margin: 0 0 12px 0; font-size: 13px; color: #6366f1; font-weight: 500; font-style: italic; line-height: 1.5; text-align: left;">
                      {selection_reason}
                    </p>
                    <div style="margin: 0 0 16px 0; font-size: 15px; color: #374151; line-height: 1.7; text-align: left;">
                      {summary_html}
                    </div>
                    <p style="margin: 0 0 8px 0; font-size: 12px; color: #6b7280; font-weight: 500; text-align: left;">
                      Copy to use with AI
                    </p>
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="padding: 14px 16px; background: #f1f5f9; border-left: 3px solid #6366f1; border-radius: 4px; text-align: left;">
                          <pre style="margin: 0; font-family: 'Courier New', Consolas, monospace; font-size: 13px; color: #1e293b; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word; text-align: left;">{escaped_prompt}</pre>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        '''

    unsubscribe_link = ""
    if recipient_email:
        encoded_email = quote(recipient_email)
        unsubscribe_link = f'<a href="https://stemem.info/unsubscribe?email={encoded_email}" style="color: #6366f1; text-decoration: none;">Unsubscribe</a>'
    else:
        unsubscribe_link = "Unsubscribe"

    email_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light dark">
  <style type="text/css">
    @media only screen and (max-width: 600px) {{
      .email-container {{
        width: 100% !important;
        padding: 20px 15px !important;
      }}
      .content-wrapper {{
        padding: 20px 15px !important;
      }}
      .paper-card {{
        padding: 18px !important;
      }}
      h1 {{
        font-size: 22px !important;
      }}
      h2 {{
        font-size: 16px !important;
      }}
      .code-block {{
        padding: 12px 14px !important;
        font-size: 12px !important;
      }}
    }}
  </style>
</head>
<body style="margin: 0; padding: 0; background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Helvetica, Arial, sans-serif;">
  <!--[if mso | IE]>
  <table align="center" border="0" cellpadding="0" cellspacing="0" style="width:600px;" width="600">
    <tr>
      <td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;">
  <![endif]-->
  <div class="email-container" style="margin: 0px auto; max-width: 600px;">
    <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="width: 100%;">
      <tbody>
        <tr>
          <td class="content-wrapper" style="direction: ltr; font-size: 0px; padding: 40px 20px; text-align: left;">
            <!--[if mso | IE]>
            <table role="presentation" border="0" cellpadding="0" cellspacing="0">
              <tr>
                <td style="vertical-align:top;width:600px;">
            <![endif]-->
            <div style="margin: 0px auto; max-width: 600px;">
              <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="width: 100%;">
                <tbody>
                  <tr>
                    <td style="direction: ltr; font-size: 0px; padding: 0; text-align: left;">
                      <div style="margin: 0px auto; max-width: 600px;">
                        <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="width: 100%;">
                          <tbody>
                            
                            <tr>
                              <td style="padding-bottom: 32px; text-align: left;">
                                <h1 style="margin: 0; font-size: 24px; font-weight: 600; color: #111827; line-height: 1.3;">
                                  everymorning
                                </h1>
                                <p style="margin: 6px 0 0 0; font-size: 14px; color: #6b7280; line-height: 1.5;">
                                  Daily STEM Paper Digest
                                </p>
                              </td>
                            </tr>
                            
                            {papers_html}
                            
                            <tr>
                              <td style="padding-top: 32px; border-top: 1px solid #e5e7eb; text-align: center;">
                                <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                                  {unsubscribe_link}
                                </p>
                              </td>
                            </tr>
                            
                          </tbody>
                        </table>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!--[if mso | IE]>
                </td>
              </tr>
            </table>
            <![endif]-->
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <!--[if mso | IE]>
      </td>
    </tr>
  </table>
  <![endif]-->
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
                    "subject": "Top3 Fresh STEM Papers",
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
