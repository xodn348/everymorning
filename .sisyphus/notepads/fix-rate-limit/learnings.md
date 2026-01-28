# Learnings - fix-rate-limit

## [2026-01-28T20:21:11] Session Start
- Plan: Fix Semantic Scholar API rate limit errors
- Error: 429 Client Error when fetching papers from multiple fields
- Root cause: Requests fire too quickly, no retry logic
