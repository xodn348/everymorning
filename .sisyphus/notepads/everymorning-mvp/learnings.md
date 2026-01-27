# Learnings - everymorning MVP

## 2026-01-27: Session Start
- Wave 1 시작: Tasks 1, 2, 3 병렬 실행
- Task 2, 3은 외부 서비스 설정 필요 (Supabase, Telegram)
- 코드 부분 먼저 진행, API 키는 나중에 설정

## Conventions
- (to be discovered)

## Gotchas
- (to be discovered)

## 2026-01-27: Task 9 - Telegram Sender Module

### Implementation
- Created `apps/pipeline/src/telegram_sender.py` following email_sender.py pattern
- Used `Bot` class directly (not `Application`) for sending-only operations
- Implemented async/sync wrapper pattern: `send_telegram_digest_async()` + `send_telegram_digest()`
- HTML parse_mode for formatted messages (bold, links)
- Error handling per chat_id with TelegramError catch

### Function Signatures
- `get_bot() -> Bot` - Initialize bot with TELEGRAM_BOT_TOKEN
- `format_digest_text(papers: List[Dict]) -> str` - Format HTML text
- `send_telegram_digest_async(chat_ids, papers) -> Dict` - Async send
- `send_telegram_digest(chat_ids, papers) -> Dict` - Sync wrapper
- Returns: `{"results": [...], "total": N, "sent": M}` (matches email_sender.py)

### Message Format
```
<b>📚 everymorning - Daily STEM Paper Digest</b>

<b>#1 {title}</b>

{summary}

<a href='{url}'>Read paper →</a>

---
```

### Dependencies
- python-telegram-bot>=21.0 (already in pyproject.toml)
- Must activate venv: `source .venv/bin/activate` before running
- Test: `python -m src.telegram_sender` generates preview (410 chars for 2 papers)

### Gotchas
- Use `Bot(token)` NOT `Application` for send-only operations
- Must use `asyncio.run()` wrapper for sync interface
- HTML entities auto-escaped by Telegram (no manual escaping needed)
- Separator logic: `if i < len(papers)` to avoid trailing separator
