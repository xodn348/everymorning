# Decisions - fix-rate-limit

## [2026-01-28T20:21:11] Retry Strategy
- Exponential backoff: 5s, 10s, 20s
- Max 3 retries before graceful degradation
- Sleep 1.5s BEFORE each request to prevent initial rate limit
