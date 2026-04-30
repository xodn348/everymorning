-- subscribers (구독자)
CREATE TABLE subscribers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE,
  telegram_chat_id TEXT UNIQUE,
  preferred_fields TEXT[] DEFAULT '{}',  -- 관심 분야 (빈 배열 = 전체 STEM)
  preferred_keywords TEXT[] DEFAULT '{}', -- 관심 키워드 최대 3개 (키워드 검색 우선)
  subscribed_at TIMESTAMPTZ DEFAULT NOW(),
  is_active BOOLEAN DEFAULT TRUE,
  CONSTRAINT subscribers_preferred_keywords_max_3 CHECK (cardinality(preferred_keywords) <= 3)
);

-- Existing deployments can migrate with:
-- ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS preferred_keywords TEXT[] DEFAULT '{}';
-- ALTER TABLE subscribers ADD CONSTRAINT subscribers_preferred_keywords_max_3 CHECK (cardinality(preferred_keywords) <= 3);
-- CREATE UNIQUE INDEX IF NOT EXISTS subscribers_active_email_unique_idx
--   ON subscribers (lower(email)) WHERE email IS NOT NULL AND is_active = TRUE;
-- CREATE UNIQUE INDEX IF NOT EXISTS subscribers_active_telegram_unique_idx
--   ON subscribers (telegram_chat_id) WHERE telegram_chat_id IS NOT NULL AND is_active = TRUE;

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

-- sent_papers (구독자별 최근 발송 이력)
CREATE TABLE sent_papers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  paper_id TEXT NOT NULL,
  subscriber_email TEXT NOT NULL,
  sent_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX sent_papers_subscriber_sent_at_idx
  ON sent_papers (subscriber_email, sent_at DESC);
