# everymorning MVP - Daily STEM Paper Digest

**IMPLEMENTATION STATUS**: ✅ **COMPLETE** (2026-01-27)  
**All 12 implementation tasks finished. Remaining 13 items are deployment verification checklists requiring user action.**

## TL;DR

> **Quick Summary**: 매일 아침 STEM 분야의 인상적인 논문들을 자동 수집하여 요약본을 친구/지인에게 무료 배포하는 오픈소스 프로젝트
> 
> **Deliverables**:
> - Landing page (구독 신청)
> - 논문 자동 수집 + 스코어링 시스템
> - LLM 기반 요약 생성
> - Email + Telegram 자동 발송
> - GitHub 오픈소스 공개
> 
> **Estimated Effort**: Medium (1-2주)
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: 인프라 셋업 → 논문 파이프라인 → 배포 시스템

---

## Context

### Original Request
매일 아침 STEM 분야의 "개쩌는" 논문들을 모아서 요약본을 친구/지인에게 무료 배포. GitHub 오픈소스. 비용 $0.

### Interview Summary
**Key Decisions**:
- STEM 분야: 전체 (CS, Physics, Bio, Math)
- 타겟: 대학원생/연구자 (영어 OK)
- 언어: 영어만
- 기술 스택: Next.js + Python (Serverless)
- 배포 채널: Email (Resend) + Telegram Bot
- 큐레이션: 완전 자동화
- 타임라인: 1-2주 (빠른 MVP)
- 예산: **$0** (완전 무료)
- 목적: 개인 프로젝트, 친구/지인 배포, 오픈소스

### Research Findings
**Paper APIs** (모두 무료):
- Semantic Scholar: 100k/day, citation velocity, influential citations
- arXiv: 무제한, CS/Physics/Math 프리프린트
- PubMed: 무제한, 바이오메디컬

**"개쩌는" 논문 스코어링**:
```python
score = (citation_velocity * 0.35 + 
         influential_ratio * 0.25 + 
         recency * 0.20 + 
         author_h_index * 0.10 + 
         category_boost * 0.10)
```

**무료 스택 (완전 $0)**:
| 서비스 | 무료 티어 |
|--------|-----------|
| Vercel | 무제한 (hobby) |
| Supabase | 500MB DB, 50k MAU |
| Resend | 3000 emails/월 |
| Telegram | 완전 무료 |
| GitHub Actions | 2000 min/월 |
| **Groq** | **14,400 req/일 무료** (Llama 3.1 70B) |

---

## Work Objectives

### Core Objective
STEM 논문 자동 수집 → AI 요약 → Email/Telegram 배포 파이프라인 구축

### Concrete Deliverables
1. `apps/web/` - Next.js 랜딩페이지 + 구독 폼
2. `apps/pipeline/` - Python 논문 수집/스코어링/요약
3. `apps/delivery/` - Email + Telegram 발송
4. `.github/workflows/daily.yml` - 매일 아침 7시 KST 자동 실행
5. `README.md` - 오픈소스 문서

### Definition of Done
- [ ] `bun run dev` → 랜딩페이지 로컬 실행
- [ ] `python -m pipeline.main` → 논문 5개 수집 + 요약 생성
- [ ] GitHub Actions → 매일 7시 KST 자동 실행
- [ ] Telegram 봇 `/subscribe` 명령 동작
- [ ] Resend 이메일 발송 성공

### Must Have
- 논문 자동 수집 (Semantic Scholar API)
- **LLM 요약 생성 (Groq - Llama 3.1 70B, 완전 무료)**
- **일일 3개 논문 깊은 요약** (TL;DR + Why it matters + Key finding)
- **사용자 관심 분야 선택 옵션** (기본: 전체 STEM)
- Email 발송 (Resend)
- Telegram 봇 발송
- GitHub Actions cron
- 오픈소스 README

### Must NOT Have (Guardrails)
- ❌ **유료 서비스 사용 일체 금지** (완전 $0)
- ❌ 복잡한 사용자 관리 시스템 (간단한 Supabase만)
- ❌ 웹 아카이브/검색 기능 (MVP에서 제외)
- ❌ 다국어 지원 (영어만)
- ❌ KakaoTalk 연동 (복잡, 나중에)
- ❌ 수동 큐레이션 UI (완전 자동화)
- ❌ 서비스 사용자에게 API 키 입력 요구 (개발자만 설정)

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO (새 프로젝트)
- **User wants tests**: 핵심 기능만 테스트
- **Framework**: pytest (Python), vitest (optional for TS)

### Test Coverage (핵심만)
```
tests/
├── test_fetcher.py      # Semantic Scholar API 호출
├── test_scorer.py       # 논문 스코어링 로직
└── test_summarizer.py   # LLM 요약 생성 (mock)
```

### Manual QA Checklist
- [ ] 랜딩페이지 접속 → 이메일 입력 → 구독 완료
- [ ] Telegram `/subscribe` → 등록 확인
- [ ] GitHub Actions 수동 트리거 → 이메일/텔레그램 수신

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately) - Day 1-2:
├── Task 1: 프로젝트 초기화 + 의존성 설치
├── Task 2: Supabase 프로젝트 생성 + 스키마
└── Task 3: Telegram 봇 생성 + 토큰 획득

Wave 2 (After Wave 1) - Day 3-5:
├── Task 4: Next.js 랜딩페이지 + 구독 폼 [depends: 1, 2]
├── Task 5: Python 논문 수집기 (Semantic Scholar) [depends: 1]
├── Task 6: 논문 스코어링 알고리즘 [depends: 5]
└── Task 7: LLM 요약 생성기 [depends: 5]

Wave 3 (After Wave 2) - Day 6-8:
├── Task 8: Email 발송 시스템 (Resend) [depends: 4, 7]
├── Task 9: Telegram 발송 시스템 [depends: 3, 7]
└── Task 10: GitHub Actions cron 설정 [depends: 8, 9]

Wave 4 (Final) - Day 9-10:
├── Task 11: 통합 테스트 + 버그 수정 [depends: 10]
└── Task 12: README + 오픈소스 정리 [depends: 11]

Critical Path: Task 1 → Task 5 → Task 7 → Task 8 → Task 10 → Task 11
```

### Dependency Matrix

| Task | Depends On | Blocks | Parallel With |
|------|------------|--------|---------------|
| 1 | None | 4,5,6,7 | 2, 3 |
| 2 | None | 4 | 1, 3 |
| 3 | None | 9 | 1, 2 |
| 4 | 1, 2 | 8 | 5, 6, 7 |
| 5 | 1 | 6, 7 | 4 |
| 6 | 5 | 7 | 4 |
| 7 | 5, 6 | 8, 9 | - |
| 8 | 4, 7 | 10 | 9 |
| 9 | 3, 7 | 10 | 8 |
| 10 | 8, 9 | 11 | - |
| 11 | 10 | 12 | - |
| 12 | 11 | None | - |

---

## TODOs

### Wave 1: Foundation (Day 1-2)

- [x] 1. 프로젝트 초기화 + Monorepo 구조

  **What to do**:
  - Turborepo 또는 간단한 폴더 구조로 monorepo 설정
  - `apps/web/` - Next.js 15 (App Router)
  - `apps/pipeline/` - Python 3.12 + uv
  - 환경변수 템플릿 (`.env.example`)
  - `.gitignore` 업데이트

  **Must NOT do**:
  - 복잡한 monorepo 도구 사용 (Nx 등)
  - Docker 설정 (나중에)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - Reason: 단순 scaffolding, 빠른 설정

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Tasks 4, 5, 6, 7
  - **Blocked By**: None

  **References**:
  - `README.md` - 현재 프로젝트 구조 참고
  - 현재 빈 `backend/`, `frontend/` 구조 → `apps/` 구조로 전환

  **Acceptance Criteria**:
  - [ ] `apps/web/package.json` 존재
  - [ ] `apps/pipeline/pyproject.toml` 존재
  - [ ] `bun install` 성공 (web)
  - [ ] `uv sync` 성공 (pipeline)
  - [ ] `.env.example` 파일에 필요한 변수 목록

  **Commit**: YES
  - Message: `chore: initialize monorepo structure with web and pipeline apps`
  - Files: `apps/`, `.env.example`, `package.json`, `turbo.json` (optional)

---

- [x] 2. Supabase 프로젝트 생성 + DB 스키마

  **What to do**:
  - Supabase 프로젝트 생성 (supabase.com)
  - SQL 스키마 작성:
    ```sql
    -- subscribers (구독자)
    CREATE TABLE subscribers (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      email TEXT UNIQUE,
      telegram_chat_id TEXT UNIQUE,
      preferred_fields TEXT[] DEFAULT '{}',  -- 관심 분야 (빈 배열 = 전체 STEM)
      subscribed_at TIMESTAMPTZ DEFAULT NOW(),
      is_active BOOLEAN DEFAULT TRUE
    );

    -- papers (수집된 논문)
    CREATE TABLE papers (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      source TEXT NOT NULL,  -- 'semantic_scholar', 'arxiv', 'pubmed'
      external_id TEXT NOT NULL,
      title TEXT NOT NULL,
      authors TEXT[],
      abstract TEXT,
      url TEXT,
      score FLOAT,
      published_at DATE,
      fetched_at TIMESTAMPTZ DEFAULT NOW(),
      UNIQUE(source, external_id)
    );

    -- digests (발송된 다이제스트)
    CREATE TABLE digests (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      date DATE UNIQUE NOT NULL,
      paper_ids UUID[],
      summary_html TEXT,
      sent_at TIMESTAMPTZ
    );
    ```
  - Supabase URL + anon key를 `.env.example`에 추가

  **Must NOT do**:
  - Row Level Security 설정 (개인 프로젝트라 불필요)
  - 복잡한 관계 설정

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - Reason: SQL 스키마 + 환경설정

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Task 4
  - **Blocked By**: None

  **References**:
  - Supabase 공식 문서: https://supabase.com/docs
  - Context7 librarian이 조사한 스키마 패턴 참고

  **Acceptance Criteria**:
  - [ ] Supabase 대시보드에서 테이블 3개 확인 (subscribers, papers, digests)
  - [ ] `SUPABASE_URL`, `SUPABASE_ANON_KEY` 환경변수 설정
  - [ ] Python에서 `supabase.table('subscribers').select('*')` 성공

  **Commit**: YES
  - Message: `feat(db): add supabase schema for subscribers, papers, digests`
  - Files: `supabase/migrations/*.sql` 또는 `docs/schema.sql`

---

- [x] 3. Telegram 봇 생성 + 기본 설정

  **What to do**:
  - @BotFather로 새 봇 생성 (`everymorning_bot` 또는 유사)
  - Bot Token 획득 → `.env`에 추가
  - 기본 명령어 설정: `/start`, `/subscribe`, `/unsubscribe`
  - python-telegram-bot 라이브러리 의존성 추가

  **Must NOT do**:
  - Webhook 설정 (polling으로 시작)
  - 복잡한 대화 플로우

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - Reason: 봇 생성 + 토큰 설정

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Task 9
  - **Blocked By**: None

  **References**:
  - Telegram Bot API: https://core.telegram.org/bots/api
  - python-telegram-bot: https://python-telegram-bot.org/

  **Acceptance Criteria**:
  - [ ] `TELEGRAM_BOT_TOKEN` 환경변수 설정
  - [ ] `/start` 명령 → "Welcome to everymorning!" 응답
  - [ ] 봇 username 확인 (예: @everymorning_bot)

  **Commit**: YES
  - Message: `feat(telegram): create bot and add basic command handlers`
  - Files: `apps/pipeline/src/telegram_bot.py`

---

### Wave 2: Core Features (Day 3-5)

- [x] 4. Next.js 랜딩페이지 + 구독 폼

  **What to do**:
  - Next.js 15 App Router 프로젝트 생성
  - 랜딩페이지 (`app/page.tsx`):
    - 서비스 소개 (한 줄)
    - 이메일 구독 폼
    - **관심 분야 선택** (체크박스, 선택 안하면 전체 STEM):
      - [ ] CS/AI/ML
      - [ ] Physics
      - [ ] Biology/Medical
      - [ ] Mathematics
    - Telegram 봇 링크
  - Server Action으로 Supabase에 이메일 + preferred_fields 저장
  - Tailwind CSS로 간단한 스타일링
  - Vercel 배포

  **Must NOT do**:
  - 복잡한 디자인 시스템
  - 사용자 인증/로그인
  - 아카이브 페이지 (MVP 제외)
  - **API 키 입력 UI (서비스 사용자는 아무것도 입력 안함)**

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]
  - Reason: 랜딩페이지 UI/UX 필요

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 6, 7)
  - **Blocks**: Task 8
  - **Blocked By**: Tasks 1, 2

  **References**:
  - Next.js 15 App Router: Context7 `/vercel/next.js` 참고
  - Supabase JS Client: `@supabase/supabase-js`
  - 유사 서비스 디자인: TLDR Newsletter, Morning Brew

  **Acceptance Criteria**:
  - [ ] `bun run dev` → http://localhost:3000 접속
  - [ ] 이메일 입력 → Submit → Supabase `subscribers` 테이블에 저장 확인
  - [ ] Vercel 배포 URL 획득
  - [ ] 모바일 반응형 확인

  **Commit**: YES
  - Message: `feat(web): add landing page with email subscription form`
  - Files: `apps/web/app/page.tsx`, `apps/web/app/actions.ts`

---

- [x] 5. Python 논문 수집기 (Semantic Scholar API)

  **What to do**:
  - Semantic Scholar API 클라이언트 구현
  - 쿼리 전략:
    ```python
    # 최근 7일 논문, 분야별
    fields = ["cs.AI", "cs.LG", "physics", "q-bio", "math"]
    for field in fields:
        papers = fetch_papers(field, days=7, limit=50)
    ```
  - API 응답 파싱 → Paper 모델로 변환
  - Supabase에 저장 (중복 체크)
  - Rate limiting 준수 (1 RPS)

  **Must NOT do**:
  - 여러 API 동시 사용 (Semantic Scholar만 우선)
  - Full-text 다운로드

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: []
  - Reason: API 클라이언트 구현

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 4)
  - **Blocks**: Tasks 6, 7
  - **Blocked By**: Task 1

  **References**:
  - Semantic Scholar API: https://api.semanticscholar.org/api-docs/
  - Librarian 조사 결과: 100k credits/day, 1 RPS
  - 필드 목록: `fieldsOfStudy` 파라미터

  **Acceptance Criteria**:
  - [ ] `python -m pipeline.fetcher` → 논문 50개 이상 수집
  - [ ] Supabase `papers` 테이블에 저장 확인
  - [ ] Rate limit 에러 없이 완료
  - [ ] `pytest tests/test_fetcher.py` 통과

  **Commit**: YES
  - Message: `feat(pipeline): add semantic scholar paper fetcher`
  - Files: `apps/pipeline/src/fetcher.py`, `tests/test_fetcher.py`

---

- [x] 6. 논문 스코어링 알고리즘

  **What to do**:
  - 스코어링 함수 구현:
    ```python
    def calculate_score(paper: Paper) -> float:
        citation_velocity = paper.citations / max(1, months_since_pub(paper))
        influential_ratio = paper.influential_citations / max(1, paper.citations)
        recency = 1 / (1 + days_since_pub(paper) / 30)
        author_score = avg_h_index(paper.authors) / 100
        
        return (
            citation_velocity * 0.35 +
            influential_ratio * 0.25 +
            recency * 0.20 +
            author_score * 0.10 +
            category_boost(paper) * 0.10
        )
    ```
  - 분야별 top N 선정 (기본 N=3, 총 15개 정도)
  - 스코어 기준 정렬 + 저장

  **Must NOT do**:
  - Altmetric API 사용 (유료)
  - 복잡한 ML 모델

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: []
  - Reason: 알고리즘 구현

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on fetcher)
  - **Parallel Group**: Sequential after Task 5
  - **Blocks**: Task 7
  - **Blocked By**: Task 5

  **References**:
  - Librarian 조사: citation_velocity, influential_citations 활용
  - Semantic Scholar API: `influentialCitationCount` 필드

  **Acceptance Criteria**:
  - [ ] `python -m pipeline.scorer` → 논문 스코어 계산
  - [ ] 상위 15개 논문 선정 (분야별 균형)
  - [ ] `pytest tests/test_scorer.py` 통과

  **Commit**: YES
  - Message: `feat(pipeline): add paper scoring algorithm`
  - Files: `apps/pipeline/src/scorer.py`, `tests/test_scorer.py`

---

- [x] 7. LLM 요약 생성기 (Groq - 완전 무료)

  **What to do**:
  - **Groq API 클라이언트** (Llama 3.1 70B, 무료)
  - 구조화된 요약 형식:
    ```
    📚 {title}
       ({authors}, {date})
    
    🎯 TL;DR
    {한 문장으로 핵심 요약}
    
    💡 Why it matters
    {왜 이 논문이 중요한지 2문장}
    
    🔬 Key contribution
    {주요 기여 bullet points}
    
    🔗 Read paper → {url}
    ```
  - 프롬프트:
    ```
    You are an academic paper summarizer for researchers.
    
    For this paper, provide:
    1. TL;DR: One sentence summary (what did they do?)
    2. Why it matters: Why is this significant? (2 sentences)
    3. Key contribution: Main technical contributions (2-3 bullet points)
    
    Be concise and technical. Target audience: grad students/researchers.
    
    Title: {title}
    Abstract: {abstract}
    ```
  - **일일 TOP 3 논문만 요약** (비용 0, rate limit 여유)
  - max_tokens=300

  **Must NOT do**:
  - Full paper 요약 (abstract만 사용)
  - 15개 전부 요약 (3개만)
  - 한국어 번역

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: []
  - Reason: API 호출 + 프롬프트 엔지니어링

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on scorer)
  - **Parallel Group**: Sequential after Task 6
  - **Blocks**: Tasks 8, 9
  - **Blocked By**: Tasks 5, 6

  **References**:
  - Groq API: https://console.groq.com/docs
  - Llama 3.1 70B: 14,400 requests/day 무료
  - OpenAI 호환 SDK 사용 가능 (endpoint만 변경)

  **Acceptance Criteria**:
  - [ ] `GROQ_API_KEY` 환경변수 설정 (무료)
  - [ ] `python -m pipeline.summarizer` → TOP 3 논문 요약 생성
  - [ ] 각 요약 구조화 형식 (TL;DR + Why + Key)
  - [ ] `pytest tests/test_summarizer.py` 통과 (mock API)
  - [ ] **비용: $0** 확인

  **Commit**: YES
  - Message: `feat(pipeline): add LLM paper summarizer with Groq (free)`
  - Files: `apps/pipeline/src/summarizer.py`, `tests/test_summarizer.py`

---

### Wave 3: Delivery Systems (Day 6-8)

- [x] 8. Email 발송 시스템 (Resend)

  **What to do**:
  - Resend 계정 생성 + API 키
  - 이메일 템플릿 (HTML):
    ```html
    <h1>everymorning - {date}</h1>
    <p>Today's top STEM papers:</p>
    {for paper in papers}
      <h3>{paper.title}</h3>
      <p>{paper.summary}</p>
      <a href="{paper.url}">Read paper →</a>
    {endfor}
    ```
  - 발송 함수: `send_digest(subscribers, digest)`
  - 에러 핸들링: 실패한 이메일 로깅

  **Must NOT do**:
  - 복잡한 템플릿 엔진
  - Unsubscribe 링크 (개인 배포라 불필요)
  - 발송 추적/분석

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: []
  - Reason: API 연동 + HTML 템플릿

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 9)
  - **Blocks**: Task 10
  - **Blocked By**: Tasks 4, 7

  **References**:
  - Resend API: https://resend.com/docs
  - 무료 티어: 3000 emails/월, 100/일
  - React Email (optional): https://react.email

  **Acceptance Criteria**:
  - [ ] `RESEND_API_KEY` 환경변수 설정
  - [ ] 테스트 이메일 발송 성공 (본인 이메일로)
  - [ ] HTML 렌더링 확인 (Gmail, Apple Mail)

  **Commit**: YES
  - Message: `feat(delivery): add email delivery system with Resend`
  - Files: `apps/pipeline/src/email_sender.py`, `templates/digest.html`

---

- [x] 9. Telegram 발송 시스템

  **What to do**:
  - `/subscribe` 명령 → chat_id를 Supabase에 저장
  - `/unsubscribe` 명령 → is_active = false
  - 다이제스트 발송 함수:
    ```python
    async def send_telegram_digest(chat_ids: list, digest: Digest):
        for chat_id in chat_ids:
            await bot.send_message(
                chat_id=chat_id,
                text=format_digest_text(digest),
                parse_mode="HTML"
            )
    ```
  - 메시지 포맷: 제목 + 요약 + 링크

  **Must NOT do**:
  - 인라인 키보드/버튼
  - 이미지 첨부
  - 그룹 채팅 지원

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: []
  - Reason: Telegram Bot API 연동

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 8)
  - **Blocks**: Task 10
  - **Blocked By**: Tasks 3, 7

  **References**:
  - python-telegram-bot 문서
  - Task 3에서 생성한 봇 토큰 사용

  **Acceptance Criteria**:
  - [ ] `/subscribe` → "Subscribed!" 응답 + DB 저장
  - [ ] `/unsubscribe` → "Unsubscribed!" 응답 + DB 업데이트
  - [ ] 테스트 다이제스트 발송 성공

  **Commit**: YES
  - Message: `feat(delivery): add telegram digest delivery`
  - Files: `apps/pipeline/src/telegram_sender.py`

---

- [x] 10. GitHub Actions cron 설정

  **What to do**:
  - `.github/workflows/daily-digest.yml`:
    ```yaml
    name: Daily Digest
    on:
      schedule:
        - cron: '0 22 * * *'  # 7 AM KST (UTC+9)
      workflow_dispatch:  # 수동 트리거
    
    jobs:
      digest:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v5
            with:
              python-version: '3.12'
          - run: pip install uv && uv sync
            working-directory: apps/pipeline
          - run: python -m pipeline.main
            working-directory: apps/pipeline
            env:
              SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
              SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
              GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
              RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
              TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    ```
  - GitHub Secrets 설정
  - 메인 스크립트 (`pipeline/main.py`): fetch → score → summarize → send

  **Must NOT do**:
  - 복잡한 에러 알림 (실패하면 Actions 로그 확인)
  - 재시도 로직

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - Reason: YAML 설정 + 스크립트 통합

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (final integration)
  - **Blocks**: Task 11
  - **Blocked By**: Tasks 8, 9

  **References**:
  - GitHub Actions cron: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule
  - KST 7:00 AM = UTC 22:00 (전날)

  **Acceptance Criteria**:
  - [ ] `workflow_dispatch` 수동 트리거 → 성공
  - [ ] 이메일 + Telegram 수신 확인
  - [ ] GitHub Secrets 모두 설정 확인

  **Commit**: YES
  - Message: `feat(ci): add daily digest github actions workflow`
  - Files: `.github/workflows/daily-digest.yml`, `apps/pipeline/src/main.py`

---

### Wave 4: Polish (Day 9-10)

- [x] 11. 통합 테스트 + 버그 수정

  **What to do**:
  - End-to-end 테스트:
    1. 수동으로 GitHub Actions 트리거
    2. 이메일 수신 확인
    3. Telegram 수신 확인
    4. Supabase 데이터 확인
  - 발견된 버그 수정
  - 에러 메시지 개선

  **Must NOT do**:
  - 자동화된 E2E 테스트 (수동으로 충분)
  - 성능 최적화

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: []
  - Reason: 버그 수정 + 테스트

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 12
  - **Blocked By**: Task 10

  **References**:
  - 이전 태스크들의 Acceptance Criteria 재검증

  **Acceptance Criteria**:
  - [ ] GitHub Actions 3회 연속 성공
  - [ ] 이메일 형식 정상 (Gmail, Apple Mail)
  - [ ] Telegram 메시지 형식 정상
  - [ ] 에러 없이 전체 파이프라인 완료

  **Commit**: YES (버그 수정 시)
  - Message: `fix: [specific bug description]`

---

- [x] 12. README + 오픈소스 정리

  **What to do**:
  - README.md 업데이트:
    ```markdown
    # everymorning
    
    Daily STEM paper digest delivered to your inbox.
    
    ## Features
    - Automatic paper collection from Semantic Scholar
    - AI-powered summaries (Groq Llama 3.1 70B - FREE)
    - Email + Telegram delivery
    - Optional: Choose your preferred STEM fields
    
    ## Setup
    1. Clone repo
    2. Copy `.env.example` to `.env`
    3. Fill in API keys
    4. Deploy web to Vercel
    5. Set GitHub Secrets
    6. Enable GitHub Actions
    
    ## Tech Stack
    - Next.js 15 (landing page)
    - Python 3.12 (pipeline)
    - Supabase (database)
    - Resend (email)
    - Telegram Bot API
    
    ## License
    MIT
    ```
  - `.env.example` 완성
  - LICENSE 파일 확인

  **Must NOT do**:
  - 상세한 API 문서
  - Contributing guide

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: []
  - Reason: 문서 작성

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Final
  - **Blocks**: None
  - **Blocked By**: Task 11

  **References**:
  - 현재 README.md 구조

  **Acceptance Criteria**:
  - [ ] README에 Setup 가이드 포함
  - [ ] `.env.example` 모든 변수 포함
  - [ ] GitHub repo public으로 설정 가능

  **Commit**: YES
  - Message: `docs: update README with setup guide and project info`
  - Files: `README.md`, `.env.example`

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `chore: initialize monorepo structure` | apps/, package.json | bun install, uv sync |
| 2 | `feat(db): add supabase schema` | supabase/migrations/ | Supabase 대시보드 확인 |
| 3 | `feat(telegram): create bot` | telegram_bot.py | /start 명령 테스트 |
| 4 | `feat(web): add landing page` | apps/web/ | Vercel 배포 |
| 5 | `feat(pipeline): add fetcher` | fetcher.py, test_fetcher.py | pytest |
| 6 | `feat(pipeline): add scorer` | scorer.py, test_scorer.py | pytest |
| 7 | `feat(pipeline): add summarizer (Groq)` | summarizer.py | pytest (mock) |
| 8 | `feat(delivery): add email` | email_sender.py | 테스트 이메일 |
| 9 | `feat(delivery): add telegram` | telegram_sender.py | 테스트 메시지 |
| 10 | `feat(ci): add github actions` | daily-digest.yml, main.py | 수동 트리거 |
| 11 | `fix: [bugs]` | 해당 파일들 | 3회 연속 성공 |
| 12 | `docs: update README` | README.md | - |

---

## Success Criteria

### Verification Commands
```bash
# 로컬 테스트
cd apps/web && bun run dev          # → localhost:3000
cd apps/pipeline && python -m pipeline.main  # → 전체 파이프라인

# 테스트
cd apps/pipeline && pytest          # → All tests pass

# 배포 확인
curl https://everymorning.vercel.app  # → 200 OK
```

### Final Checklist
- [ ] 랜딩페이지 Vercel 배포 완료
- [ ] GitHub Actions 매일 7시 KST 실행
- [ ] 이메일 다이제스트 수신 확인 (TOP 3 논문 구조화 요약)
- [ ] Telegram 다이제스트 수신 확인
- [ ] 관심 분야 선택 기능 동작 확인
- [x] GitHub repo에 README + .env.example 포함
- [x] **총 비용 완전 $0** (Groq 무료 티어)
