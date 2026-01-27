import sys
from datetime import datetime
from typing import List, Dict, Any

from src.fetcher import fetch_all_fields
from src.scorer import get_top_papers
from src.summarizer import summarize_papers
from src.email_sender import send_digest_email
from src.telegram_sender import send_telegram_digest
from src.db import get_supabase_client


def log(message: str) -> None:
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {message}")


def get_subscribers() -> tuple[List[str], List[str]]:
    try:
        supabase = get_supabase_client()
        result = supabase.table("subscribers").select("email,telegram_chat_id").eq("is_active", True).execute()
        
        emails = []
        chat_ids = []
        
        if result.data:
            for subscriber in result.data:
                if subscriber.get("email"):
                    emails.append(subscriber["email"])
                if subscriber.get("telegram_chat_id"):
                    chat_ids.append(str(subscriber["telegram_chat_id"]))
        
        log(f"Retrieved {len(emails)} email subscribers and {len(chat_ids)} Telegram subscribers")
        return emails, chat_ids
    except Exception as e:
        log(f"Error fetching subscribers: {e}")
        return [], []


def main():
    log("Starting daily digest pipeline")
    
    papers_with_summaries = []
    
    try:
        log("Step 1: Fetching papers from all STEM fields")
        papers = fetch_all_fields(days=7, limit_per_field=50)
        log(f"Fetched {len(papers)} papers")
    except Exception as e:
        log(f"Error fetching papers: {e}")
        return 1
    
    try:
        log("Step 2: Scoring and selecting top 3 papers")
        top_papers = get_top_papers(papers, n=3)
        log(f"Selected {len(top_papers)} top papers")
    except Exception as e:
        log(f"Error scoring papers: {e}")
        return 1
    
    try:
        log("Step 3: Generating summaries for top papers")
        papers_with_summaries = summarize_papers(top_papers, max_papers=3)
        log(f"Generated summaries for {len(papers_with_summaries)} papers")
    except Exception as e:
        log(f"Error summarizing papers: {e}")
        return 1
    
    try:
        log("Step 4: Fetching subscribers from database")
        emails, chat_ids = get_subscribers()
    except Exception as e:
        log(f"Error fetching subscribers: {e}")
        emails, chat_ids = [], []
    
    if not emails and not chat_ids:
        log("No subscribers found, skipping sending")
        return 0
    
    if emails:
        try:
            log(f"Step 5: Sending email digest to {len(emails)} subscribers")
            email_result = send_digest_email(emails, papers_with_summaries)
            log(f"Email result: {email_result['sent']}/{email_result['total']} sent")
        except Exception as e:
            log(f"Error sending emails: {e}")
    
    if chat_ids:
        try:
            log(f"Step 6: Sending Telegram digest to {len(chat_ids)} subscribers")
            telegram_result = send_telegram_digest(chat_ids, papers_with_summaries)
            log(f"Telegram result: {telegram_result['sent']}/{telegram_result['total']} sent")
        except Exception as e:
            log(f"Error sending Telegram messages: {e}")
    
    log("Daily digest pipeline completed successfully")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
