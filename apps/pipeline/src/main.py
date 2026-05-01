import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any

from src.fetcher import fetch_all_fields, fetch_papers_for_keywords
from src.scorer import score_papers, select_personalized_papers, normalize_keywords
from src.summarizer import summarize_papers
from src.email_sender import send_digest_email
from src.telegram_sender import send_telegram_digest
from src.db import get_supabase_client, get_recently_sent_paper_ids, save_sent_papers


def log(message: str) -> None:
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {message}")


def merge_unique(values: List[str]) -> List[str]:
    merged = []
    for value in values:
        if value and value not in merged:
            merged.append(value)
    return merged


def dedupe_subscribers(subscribers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Collapse duplicate active subscribers, preferring rows with keywords."""
    by_email: Dict[str, Dict[str, Any]] = {}
    passthrough: List[Dict[str, Any]] = []

    for subscriber in subscribers:
        email = (subscriber.get("email") or "").strip().lower()
        subscriber["email"] = email or subscriber.get("email")
        if not email:
            passthrough.append(subscriber)
            continue

        existing = by_email.get(email)
        if not existing:
            by_email[email] = subscriber
            continue

        existing_has_keywords = bool(existing.get("preferred_keywords"))
        subscriber_has_keywords = bool(subscriber.get("preferred_keywords"))
        if subscriber_has_keywords and not existing_has_keywords:
            keeper, other = subscriber, existing
        else:
            keeper, other = existing, subscriber
        keeper["preferred_fields"] = merge_unique(
            (keeper.get("preferred_fields") or []) + (other.get("preferred_fields") or [])
        )
        keeper["preferred_keywords"] = merge_unique(
            (keeper.get("preferred_keywords") or []) + (other.get("preferred_keywords") or [])
        )[:3]
        by_email[email] = keeper

    deduped = list(by_email.values()) + passthrough
    if len(deduped) != len(subscribers):
        log(f"Deduped active subscribers from {len(subscribers)} to {len(deduped)}")
    return deduped


def get_subscribers() -> List[Dict[str, Any]]:
    try:
        supabase = get_supabase_client()
        try:
            result = (
                supabase.table("subscribers")
                .select("id,email,telegram_chat_id,preferred_fields,preferred_keywords")
                .eq("is_active", True)
                .execute()
            )
        except Exception as e:
            if "preferred_keywords" not in str(e):
                raise
            log("preferred_keywords column not found; using legacy subscriber fields")
            result = (
                supabase.table("subscribers")
                .select("id,email,telegram_chat_id,preferred_fields")
                .eq("is_active", True)
                .execute()
            )

        subscribers = []
        if result.data:
            for row in result.data:
                subscribers.append(
                    {
                        "id": row.get("id"),
                        "email": (row.get("email") or "").strip().lower() or None,
                        "telegram_chat_id": str(row["telegram_chat_id"])
                        if row.get("telegram_chat_id")
                        else None,
                        "preferred_fields": row.get("preferred_fields") or [],
                        "preferred_keywords": normalize_keywords(
                            row.get("preferred_keywords") or []
                        ),
                    }
                )

        subscribers = dedupe_subscribers(subscribers)
        log(f"Retrieved {len(subscribers)} active subscribers")
        return subscribers
    except Exception as e:
        log(f"Error fetching subscribers: {e}")
        return []


def unique_keywords(subscribers: List[Dict[str, Any]]) -> List[str]:
    keywords = []
    for subscriber in subscribers:
        for keyword in normalize_keywords(subscriber.get("preferred_keywords") or []):
            if keyword not in keywords:
                keywords.append(keyword)
    return keywords


def fallback_fields(subscribers: List[Dict[str, Any]]) -> List[str]:
    """
    Return fallback domains to fetch. Empty means fetch all STEM domains.
    If any subscriber has no selected domains, all domains are needed for that subscriber.
    """
    fields = []
    for subscriber in subscribers:
        preferred = subscriber.get("preferred_fields") or []
        if not preferred:
            return []
        for field in preferred:
            if field not in fields:
                fields.append(field)
    return fields


def flatten_keyword_results(
    keywords: List[str], keyword_results: Dict[str, List[Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    papers = []
    for keyword in keywords:
        papers.extend(keyword_results.get(keyword, []))
    return papers


def build_summary_map(papers: List[Dict[str, Any]], dry_run: bool) -> Dict[str, Dict[str, Any]]:
    unique = {}
    for paper in papers:
        paper_id = paper.get("paperId")
        if paper_id and paper_id not in unique:
            unique[paper_id] = paper

    if dry_run:
        return {
            paper_id: {**paper, "summary": paper.get("summary", "Dry run: summary skipped")}
            for paper_id, paper in unique.items()
        }

    summarized = summarize_papers(list(unique.values()), max_papers=len(unique))
    return {paper.get("paperId"): paper for paper in summarized if paper.get("paperId")}


def attach_summaries(
    selected_by_subscriber: List[Dict[str, Any]], summary_map: Dict[str, Dict[str, Any]]
) -> None:
    for digest in selected_by_subscriber:
        summarized = []
        for paper in digest["papers"]:
            paper_id = paper.get("paperId")
            merged = {**paper, **summary_map.get(paper_id, {})}
            merged["selection_reason"] = paper.get("selection_reason")
            merged["category"] = paper.get("category")
            merged["selection_category"] = paper.get("selection_category")
            summarized.append(merged)
        digest["papers"] = summarized


def filter_subscribers_by_email(
    subscribers: List[Dict[str, Any]], only_email: str | None
) -> List[Dict[str, Any]]:
    if not only_email:
        return subscribers

    target = only_email.strip().lower()
    filtered = [
        subscriber
        for subscriber in subscribers
        if (subscriber.get("email") or "").strip().lower() == target
    ]
    log(f"Filtered subscribers to {len(filtered)} matching {target}")
    return filtered


def main():
    parser = argparse.ArgumentParser(description="Daily STEM digest pipeline")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be sent without actually sending",
    )
    parser.add_argument(
        "--only-email",
        help="Send or dry-run the digest for one subscriber email only",
    )
    args = parser.parse_args()

    log("Starting daily digest pipeline")

    try:
        log("Step 1: Fetching subscribers")
        subscribers = filter_subscribers_by_email(get_subscribers(), args.only_email)
    except Exception as e:
        log(f"Error fetching subscribers: {e}")
        return 1

    if not subscribers:
        log("No subscribers found, skipping sending")
        return 0

    keywords = unique_keywords(subscribers)
    fields = fallback_fields(subscribers)

    try:
        log(f"Step 2: Searching {len(keywords)} unique subscriber keywords")
        keyword_results = fetch_papers_for_keywords(
            keywords, days=180, limit_per_keyword=20
        )
        keyword_papers = flatten_keyword_results(keywords, keyword_results)
        log(f"Fetched {len(keyword_papers)} keyword papers")
    except Exception as e:
        log(f"Error fetching keyword papers: {e}")
        keyword_results = {}
        keyword_papers = []

    try:
        fallback_label = ", ".join(fields) if fields else "all STEM domains"
        log(f"Step 3: Fetching fallback papers from {fallback_label}")
        fallback_papers = fetch_all_fields(
            days=180, limit_per_field=50, fields=fields or None
        )
        log(f"Fetched {len(fallback_papers)} fallback papers")
    except Exception as e:
        log(f"Error fetching fallback papers: {e}")
        fallback_papers = []

    try:
        log("Step 4: Scoring papers")
        score_papers(keyword_papers)
        scored_fallback_papers = score_papers(fallback_papers)
    except Exception as e:
        log(f"Error scoring papers: {e}")
        return 1

    selected_by_subscriber = []
    all_selected = []

    for subscriber in subscribers:
        preferred_fields = subscriber.get("preferred_fields") or []
        preferred_keywords = subscriber.get("preferred_keywords") or []
        subscriber_keyword_papers = flatten_keyword_results(
            preferred_keywords, keyword_results
        )
        subscriber_keyword_papers = score_papers(subscriber_keyword_papers)

        if subscriber.get("email"):
            sent_ids = get_recently_sent_paper_ids(subscriber["email"])
        else:
            sent_ids = []

        personalized = select_personalized_papers(
            subscriber_keyword_papers,
            scored_fallback_papers,
            preferred_fields,
            preferred_keywords,
            sent_ids,
            n=3,
        )

        if not personalized:
            log(
                f"No fresh papers for subscriber with keywords {preferred_keywords} and fields {preferred_fields}; sending empty digest"
            )

        selected_by_subscriber.append({"subscriber": subscriber, "papers": personalized})
        all_selected.extend(personalized)

    try:
        selected_paper_ids = {
            p.get("paperId") for p in all_selected if p.get("paperId")
        }
        log(f"Step 5: Summarizing {len(selected_paper_ids)} unique selected papers")
        summary_map = build_summary_map(all_selected, dry_run=args.dry_run)
        attach_summaries(selected_by_subscriber, summary_map)
    except Exception as e:
        log(f"Error summarizing papers: {e}")
        return 1

    email_sent = 0
    telegram_sent = 0

    for digest in selected_by_subscriber:
        subscriber = digest["subscriber"]
        personalized = digest["papers"]

        if args.dry_run:
            email = subscriber.get("email") or "(no email)"
            chat_id = subscriber.get("telegram_chat_id") or "(no telegram)"
            fields_str = ", ".join(subscriber.get("preferred_fields") or []) or "all fields"
            keywords_str = ", ".join(subscriber.get("preferred_keywords") or []) or "none"

            print(f"\n{'=' * 60}")
            print(f"SUBSCRIBER: {email} | Telegram: {chat_id}")
            print(f"KEYWORDS: {keywords_str}")
            print(f"FALLBACK DOMAINS: {fields_str}")
            print(f"PAPERS ({len(personalized)}):")
            for i, paper in enumerate(personalized, 1):
                print(
                    f"  {i}. [{paper.get('field', '?')}] {paper.get('title', 'Unknown')[:80]}"
                )
                print(f"     {paper.get('selection_reason', '')}")
            continue

        if subscriber.get("email"):
            try:
                result = send_digest_email([subscriber["email"]], personalized)
                sent_count = result.get("sent", 0)
                email_sent += sent_count
                if sent_count > 0 and personalized:
                    sent_paper_ids = [
                        p.get("paperId") for p in personalized if p.get("paperId")
                    ]
                    save_sent_papers(sent_paper_ids, subscriber["email"])
                elif sent_count == 0:
                    log("Email delivery failed; not marking papers as sent")
            except Exception as e:
                log(f"Error sending email: {e}")

        if subscriber.get("telegram_chat_id"):
            try:
                result = send_telegram_digest([subscriber["telegram_chat_id"]], personalized)
                telegram_sent += result.get("sent", 0)
            except Exception as e:
                log(f"Error sending telegram: {e}")

    log(f"Sent {email_sent} emails and {telegram_sent} Telegram messages")
    log("Daily digest pipeline completed successfully")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
