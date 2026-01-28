# Fix Semantic Scholar Rate Limit Error

## TL;DR

> **Quick Summary**: Add exponential backoff retry logic to handle 429 rate limit errors from Semantic Scholar API
> 
> **Deliverables**:
> - Updated `fetcher.py` with retry logic
> - Passing GitHub Actions workflow
> 
> **Estimated Effort**: Quick
> **Parallel Execution**: NO - sequential
> **Critical Path**: Task 1 → Task 2 → Task 3

---

## Context

### Original Request
GitHub Actions workflow failed with 429 rate limit error from Semantic Scholar API. The pipeline fetches papers from multiple fields (cs, physics, bio, math) and the API rejects requests when they come too fast.

### Error Log
```
Error fetching papers: 429 Client Error: for url: https://api.semanticscholar.org/graph/v1/paper/search?query=Physics...
```

### Root Cause
- `fetch_all_fields()` has `time.sleep(1)` but it's placed AFTER the request
- First two requests (cs, physics) fire in quick succession
- No retry mechanism for 429 errors

---

## Work Objectives

### Core Objective
Make the paper fetching resilient to rate limits with exponential backoff retry.

### Concrete Deliverables
- `apps/pipeline/src/fetcher.py` - Updated with retry logic

### Definition of Done
- [ ] GitHub Actions workflow passes
- [ ] Papers are fetched successfully

### Must Have
- Exponential backoff on 429 errors (5s, 10s, 20s)
- Max 3 retries before giving up gracefully
- Sleep BEFORE each request, not just after

### Must NOT Have (Guardrails)
- No external rate limiting libraries
- Don't change the API endpoint or parameters
- Don't reduce the number of fields fetched

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO (no test framework in pipeline)
- **User wants tests**: NO - Manual verification via GitHub Actions
- **QA approach**: Trigger workflow and verify success

---

## TODOs

- [ ] 1. Add exponential backoff retry to fetch_papers_by_field()

  **What to do**:
  - Wrap the API request in a retry loop (max 3 attempts)
  - On 429 status code, wait with exponential backoff: 5s, 10s, 20s
  - After all retries fail, return empty list (graceful degradation)
  - Add sleep(1.5) BEFORE each request to prevent hitting rate limit

  **Must NOT do**:
  - Don't import any new packages (requests + time already available)
  - Don't change the return type or signature

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
    - No special skills needed - simple Python edit

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 2
  - **Blocked By**: None

  **References**:
  - `apps/pipeline/src/fetcher.py:19-45` - Current `fetch_papers_by_field()` function
  - `apps/pipeline/src/fetcher.py:48-64` - `fetch_all_fields()` shows current sleep pattern

  **Code Change**:
  ```python
  def fetch_papers_by_field(field: str, days: int = 7, limit: int = 50, max_retries: int = 3) -> List[Dict[str, Any]]:
      """
      Fetch recent papers from Semantic Scholar API by field
      Rate limit: 1 request per second with exponential backoff on 429
      """
      url = f"{SEMANTIC_SCHOLAR_API}/paper/search"

      # Papers from last N days
      date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

      params = {
          "query": FIELD_MAPPING.get(field, field),
          "fields": "paperId,title,abstract,authors,citationCount,influentialCitationCount,publicationDate,url,fieldsOfStudy",
          "limit": limit,
          "publicationDateOrYear": f"{date_from}:",
      }

      headers = {}
      api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
      if api_key:
          headers["x-api-key"] = api_key

      for attempt in range(max_retries):
          # Rate limit: wait before request
          time.sleep(1.5)
          
          response = requests.get(url, params=params, headers=headers)
          
          if response.status_code == 429:
              # Rate limited - exponential backoff
              wait_time = (2 ** attempt) * 5  # 5s, 10s, 20s
              print(f"Rate limited, waiting {wait_time}s before retry...")
              time.sleep(wait_time)
              continue
          
          response.raise_for_status()
          data = response.json()
          return data.get("data", [])
      
      # All retries exhausted - graceful degradation
      print(f"Failed to fetch {field} papers after {max_retries} retries")
      return []
  ```

  **Acceptance Criteria**:
  - [ ] Function has `max_retries` parameter with default 3
  - [ ] Loop wraps API request with retry logic
  - [ ] 429 status triggers exponential backoff (5s, 10s, 20s)
  - [ ] Returns empty list on exhausted retries (no crash)

  **Commit**: YES
  - Message: `fix(fetcher): add exponential backoff for rate limit errors`
  - Files: `apps/pipeline/src/fetcher.py`

---

- [ ] 2. Commit and push changes

  **What to do**:
  - Commit the fetcher.py changes
  - Push to origin/main

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`git-master`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Task 1
  - **Blocks**: Task 3

  **Acceptance Criteria**:
  - [ ] `git status` shows clean working tree
  - [ ] `git log -1` shows the new commit

  **Commit**: Already specified in Task 1

---

- [ ] 3. Trigger GitHub Actions workflow and verify success

  **What to do**:
  - Run `gh workflow run daily-digest.yml`
  - Watch the workflow with `gh run watch <id> --exit-status`
  - Verify it completes successfully

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Task 2
  - **Blocks**: None

  **Acceptance Criteria**:
  - [ ] `gh run list --limit 1` shows status "completed" with conclusion "success"
  - [ ] Workflow logs show papers fetched from all fields

---

## Success Criteria

### Verification Commands
```bash
# Verify workflow passes
gh run list --limit 1  # Expected: status=completed, conclusion=success
```

### Final Checklist
- [ ] fetch_papers_by_field() has retry logic
- [ ] GitHub Actions workflow passes
- [ ] Email/Telegram digest is sent successfully
