import os
import html
import asyncio
from typing import List, Dict, Any
from telegram import Bot
from telegram.error import TelegramError


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


def get_bot() -> Bot:
    """Initialize Telegram Bot."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN must be set")
    return Bot(token=token)


def mask_id(chat_id: str) -> str:
    """Mask chat_id for logging (show first 3 and last 2 digits)."""
    if len(chat_id) > 5:
        return f"{chat_id[:3]}***{chat_id[-2:]}"
    return "***"


def format_digest_text(papers: List[Dict[str, Any]]) -> str:
    text = "<b>everymorning - Daily STEM Paper Digest</b>\n\n"

    for i, paper in enumerate(papers, 1):
        title = html.escape(paper.get("title", "Unknown"))
        raw_summary = paper.get("summary", "No summary available")

        summary_lines = []
        for line in raw_summary.split("\n"):
            line = line.strip()
            if line:
                summary_lines.append(html.escape(line))
        summary = "\n".join(summary_lines)

        url = html.escape(paper.get("url", ""))
        selection_reason = html.escape(paper.get("selection_reason", ""))
        field = paper.get("field", "")

        text += f"<b>#{i} {title}</b>\n"
        if selection_reason:
            text += f"<i>{selection_reason}</i>\n"
        text += "\n"
        text += f"{summary}\n\n"

        if url:
            text += f"<a href='{url}'>Read paper</a>\n"

        ai_prompt = generate_ai_prompt(
            paper.get("title", ""),
            field,
            paper.get("summary", ""),
            paper.get("url", ""),
        )
        escaped_prompt = html.escape(ai_prompt)
        text += f"\n<pre>{escaped_prompt}</pre>\n\n"

        if i < len(papers):
            text += "---\n\n"

    return text


async def send_telegram_digest_async(
    chat_ids: List[str], papers: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Send digest to Telegram subscribers (async version)."""
    bot = get_bot()
    text = format_digest_text(papers)

    results = []
    for chat_id in chat_ids:
        masked_id = mask_id(chat_id)
        try:
            message = await bot.send_message(
                chat_id=chat_id, text=text, parse_mode="HTML"
            )
            results.append(
                {"chat_id": chat_id, "status": "sent", "message_id": message.message_id}
            )
            print(f"Message sent to {masked_id}")
        except TelegramError as e:
            results.append(
                {"chat_id": chat_id, "status": "failed", "error": "Telegram error"}
            )
            print(f"Failed to send to {masked_id}")
        except Exception as e:
            results.append(
                {"chat_id": chat_id, "status": "failed", "error": "Send error"}
            )
            print(f"Unexpected error for {masked_id}")

    return {
        "results": results,
        "total": len(chat_ids),
        "sent": sum(1 for r in results if r["status"] == "sent"),
    }


def send_telegram_digest(
    chat_ids: List[str], papers: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Send digest to Telegram subscribers (sync wrapper)."""
    return asyncio.run(send_telegram_digest_async(chat_ids, papers))


def main():
    test_papers = [
        {
            "title": "Test Paper 1: Machine Learning Advances",
            "summary": "This paper explores novel approaches to deep learning optimization.",
            "url": "https://example.com/paper1",
            "field": "cs",
            "selection_reason": "Relevant to your interests",
        }
    ]

    text = format_digest_text(test_papers)
    print("Telegram Digest Preview:")
    print("=" * 60)
    print(text)
    print("=" * 60)
    print(f"Message length: {len(text)} characters")


if __name__ == "__main__":
    main()
