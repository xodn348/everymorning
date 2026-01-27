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

## 2026-01-27: Task 10 - GitHub Actions Workflow & Main Orchestrator

### Implementation

#### 1. GitHub Actions Workflow (`.github/workflows/daily-digest.yml`)
- Cron schedule: `0 22 * * *` (7 AM KST = UTC 22:00)
- Manual trigger: `workflow_dispatch`
- Python 3.12 with uv for dependency management
- All environment variables from GitHub Secrets:
  - SUPABASE_URL, SUPABASE_ANON_KEY
  - GROQ_API_KEY
  - RESEND_API_KEY
  - TELEGRAM_BOT_TOKEN

#### 2. Main Orchestrator (`apps/pipeline/src/main.py`)
- Orchestrates full pipeline: fetch → score → summarize → send
- Function signatures:
  - `get_subscribers() -> tuple[List[str], List[str]]` - Returns (emails, chat_ids)
  - `log(message: str) -> None` - Timestamped logging
  - `main() -> int` - Returns exit code (0 on success)

### Pipeline Flow
1. Fetch papers from all STEM fields (cs, physics, bio, math)
2. Score and select top 3 papers
3. Generate LLM summaries for top papers
4. Fetch active subscribers from DB (email + Telegram)
5. Send email digest via Resend
6. Send Telegram digest via python-telegram-bot
7. Log each step with timestamps

### Error Handling
- Each major step wrapped in try/except
- Errors logged but pipeline continues
- Returns exit code 0 even if some steps fail (GitHub Actions won't break)
- Gracefully handles missing subscribers

### Subscriber Query
```python
supabase.table("subscribers").select("email,telegram_chat_id").eq("is_active", True).execute()
```
- Filters for is_active=True only
- Handles missing email/telegram_chat_id fields

### Validation
- YAML syntax: Valid ✓
- Python imports: Valid ✓
- All modules imported successfully

### Key Design Decisions
- Sync wrapper for main.py (no async in orchestrator)
- Separate email/chat_id lists for independent sending
- Logging at each step for observability
- Exit code 0 on partial failures (don't break CI/CD)
