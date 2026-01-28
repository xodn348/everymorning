import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any

from src.fetcher import fetch_all_fields
from src.scorer import score_papers, get_personalized_papers
from src.summarizer import summarize_papers
from src.email_sender import send_digest_email
from src.telegram_sender import send_telegram_digest
from src.db import get_supabase_client


def log(message: str) -> None:
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {message}")


def get_subscribers() -> List[Dict[str, Any]]:
    try:
        supabase = get_supabase_client()
        result = (
            supabase.table("subscribers")
            .select("email,telegram_chat_id,preferred_fields")
            .eq("is_active", True)
            .execute()
        )

        subscribers = []
        if result.data:
            for row in result.data:
                subscribers.append(
                    {
                        "email": row.get("email"),
                        "telegram_chat_id": str(row["telegram_chat_id"])
                        if row.get("telegram_chat_id")
                        else None,
                        "preferred_fields": row.get("preferred_fields") or [],
                    }
                )

        log(f"Retrieved {len(subscribers)} active subscribers")
        return subscribers
    except Exception as e:
        log(f"Error fetching subscribers: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Daily STEM digest pipeline")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be sent without actually sending",
    )
    args = parser.parse_args()

    log("Starting daily digest pipeline")

    try:
        log("Step 1: Fetching papers from all STEM fields")
        papers = fetch_all_fields(days=7, limit_per_field=50)
        log(f"Fetched {len(papers)} papers")
    except Exception as e:
        log(f"Error fetching papers: {e}")
        return 1

    try:
        log("Step 2: Scoring papers")
        scored_papers = score_papers(papers)
    except Exception as e:
        log(f"Error scoring papers: {e}")
        return 1

    try:
        log("Step 3: Summarizing top 30 papers")
        top_30 = scored_papers[:30]
        summarized_papers = summarize_papers(top_30, max_papers=30)
        log(f"Summarized {len(summarized_papers)} papers")
    except Exception as e:
        log(f"Error summarizing papers: {e}")
        return 1

    try:
        log("Step 4: Fetching subscribers")
        subscribers = get_subscribers()
    except Exception as e:
        log(f"Error fetching subscribers: {e}")
        return 1

    if not subscribers:
        log("No subscribers found, skipping sending")
        return 0

    # Step 5: Send personalized digests
    email_sent = 0
    telegram_sent = 0

    for subscriber in subscribers:
        # Get personalized papers for this subscriber
        preferred = subscriber.get("preferred_fields") or []
        personalized = get_personalized_papers(summarized_papers, preferred, n=3)

        if not personalized:
            log(f"No papers for subscriber with fields {preferred}, skipping")
            continue

        if args.dry_run:
            # Dry run: print instead of send
            email = subscriber.get("email") or "(no email)"
            chat_id = subscriber.get("telegram_chat_id") or "(no telegram)"
            fields_str = ", ".join(preferred) if preferred else "all fields"

            print(f"\n{'=' * 60}")
            print(f"SUBSCRIBER: {email} | Telegram: {chat_id}")
            print(f"PREFERRED FIELDS: {fields_str}")
            print(f"PAPERS ({len(personalized)}):")
            for i, p in enumerate(personalized, 1):
                print(
                    f"  {i}. [{p.get('field', '?')}] {p.get('title', 'Unknown')[:60]}..."
                )
            continue  # Skip actual sending

        # Send email if subscriber has email
        if subscriber.get("email"):
            try:
                result = send_digest_email([subscriber["email"]], personalized)
                email_sent += result.get("sent", 0)
            except Exception as e:
                log(f"Error sending email: {e}")

        # Send telegram if subscriber has chat_id
        if subscriber.get("telegram_chat_id"):
            try:
                result = send_telegram_digest(
                    [subscriber["telegram_chat_id"]], personalized
                )
                telegram_sent += result.get("sent", 0)
            except Exception as e:
                log(f"Error sending telegram: {e}")

    log(f"Sent {email_sent} emails and {telegram_sent} Telegram messages")
    log("Daily digest pipeline completed successfully")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
