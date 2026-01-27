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
