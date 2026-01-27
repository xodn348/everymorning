# everymorning 📚

> Daily STEM paper digest delivered to your inbox, completely free.

Automatically collects impressive research papers from Semantic Scholar, generates AI-powered summaries, and delivers them via email and Telegram every morning at 7 AM KST.

---

## ✨ Features

- **Automatic Paper Collection** - Fetches latest papers from Semantic Scholar across CS, Physics, Biology, and Math
- **Smart Scoring** - Ranks papers by citation velocity and influential citations to surface the most impactful research
- **AI-Powered Summaries** - Generates structured summaries (TL;DR, Why it matters, Key contributions) using Groq's Llama 3.1 70B
- **Dual Delivery** - Sends digest via email (Resend) and Telegram for maximum convenience
- **Completely Free** - All services use generous free tiers ($0 monthly cost)
- **Open Source** - MIT licensed, fully customizable

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** | Next.js (App Router) | 15.x |
| **Backend** | Python + uv | 3.12 |
| **Database** | Supabase (PostgreSQL) | Latest |
| **Email** | Resend | Latest |
| **Messaging** | Telegram Bot API | Latest |
| **LLM** | Groq (Llama 3.1 70B) | Latest |
| **CI/CD** | GitHub Actions | Latest |
| **Hosting** | Vercel (web) + GitHub Actions (pipeline) | Latest |

---

## 📋 Prerequisites

Before setting up, create free accounts for:

1. **[Supabase](https://supabase.com)** - Database (500MB free)
2. **[Resend](https://resend.com)** - Email delivery (3,000 emails/month free)
3. **[Telegram](https://t.me/botfather)** - Bot creation (unlimited free)
4. **[Groq](https://console.groq.com)** - LLM API (free tier available)
5. **[Vercel](https://vercel.com)** - Web hosting (free for hobby projects)
6. **GitHub Account** - For repository and Actions

---

## 🚀 Setup Guide

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/everymorning.git
cd everymorning
```

### 2. Set Up Database

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run this schema:

```sql
-- Papers table
CREATE TABLE papers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL,
  external_id TEXT NOT NULL,
  title TEXT NOT NULL,
  authors TEXT[],
  abstract TEXT,
  url TEXT,
  published_at DATE,
  score FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(source, external_id)
);

-- Subscribers table
CREATE TABLE subscribers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT,
  telegram_chat_id BIGINT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add yourself as a test subscriber
INSERT INTO subscribers (email, is_active)
VALUES ('your-email@example.com', TRUE);
```

3. Get your credentials from Settings → API:
   - `SUPABASE_URL` (e.g., `https://xxxxx.supabase.co`)
   - `SUPABASE_ANON_KEY` (public/anon key)

### 3. Set Up Email Delivery

1. Sign up at [resend.com](https://resend.com)
2. Get your API key from Settings → API Keys
3. (Optional) Verify your domain, or use `onboarding@resend.dev` for testing

### 4. Set Up Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot` command
3. Save the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. (Optional) Get your chat ID:
   ```bash
   # Start a chat with your bot, then:
   curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
5. Add your chat ID to Supabase:
   ```sql
   UPDATE subscribers 
   SET telegram_chat_id = YOUR_CHAT_ID 
   WHERE email = 'your-email@example.com';
   ```

### 5. Set Up Groq API

1. Sign up at [console.groq.com](https://console.groq.com)
2. Create an API key from Settings → API Keys
3. Save the key (format: `gsk_xxxxxxxxxxxxx`)

### 6. Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions → New repository secret

Add these 5 secrets:

| Secret Name | Description |
|-------------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | Your Supabase anon/public key |
| `GROQ_API_KEY` | Your Groq API key |
| `RESEND_API_KEY` | Your Resend API key |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token |

### 7. Deploy Web App (Optional)

The landing page is a Next.js app in `apps/web/`:

1. Push your repository to GitHub
2. Go to [vercel.com](https://vercel.com) and import your repository
3. Vercel will auto-detect Next.js and deploy
4. Your landing page will be live at `https://your-project.vercel.app`

### 8. Test the Pipeline

#### Manual Trigger (Recommended for First Test)

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Daily Digest** workflow
4. Click **Run workflow** → **Run workflow**
5. Wait 2-3 minutes for completion
6. Check your email and Telegram for the digest

#### Local Testing

```bash
# Install dependencies
cd apps/pipeline
pip install uv
uv sync

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Run pipeline
uv run python -m src.main
```

---

## 📖 Usage

### Automatic Daily Delivery

The pipeline runs automatically every day at **7 AM KST (10 PM UTC previous day)** via GitHub Actions.

### Manual Trigger

You can manually trigger the workflow anytime:

```bash
# Using GitHub CLI
gh workflow run daily-digest.yml

# Or via GitHub web UI (Actions tab)
```

### Add Subscribers

Add new subscribers to the Supabase `subscribers` table:

```sql
INSERT INTO subscribers (email, telegram_chat_id, is_active)
VALUES ('user@example.com', 123456789, TRUE);
```

- `email`: Email address (optional if telegram_chat_id provided)
- `telegram_chat_id`: Telegram chat ID (optional if email provided)
- `is_active`: Set to `FALSE` to pause delivery

---

## 📁 Project Structure

```
everymorning/
├── apps/
│   ├── web/                    # Next.js landing page
│   │   ├── app/                # App Router pages
│   │   ├── components/         # React components
│   │   └── public/             # Static assets
│   └── pipeline/               # Python digest pipeline
│       ├── src/
│       │   ├── db.py           # Supabase client
│       │   ├── fetcher.py      # Semantic Scholar API
│       │   ├── scorer.py       # Paper scoring logic
│       │   ├── summarizer.py   # Groq LLM summaries
│       │   ├── email_sender.py # Resend email delivery
│       │   ├── telegram_sender.py # Telegram delivery
│       │   └── main.py         # Pipeline orchestrator
│       ├── pyproject.toml      # Python dependencies
│       └── .env.example        # Environment template
├── .github/
│   └── workflows/
│       └── daily-digest.yml    # GitHub Actions workflow
├── supabase/
│   └── schema.sql              # Database schema
├── .sisyphus/                  # Development notes
│   └── notepads/
│       └── everymorning-mvp/
│           ├── learnings.md    # Implementation notes
│           └── TESTING.md      # Integration testing guide
└── README.md                   # This file
```

---

## 💰 Cost Breakdown

All services use generous free tiers:

| Service | Free Tier | Monthly Cost |
|---------|-----------|--------------|
| **Semantic Scholar API** | 100,000 requests/day | $0 |
| **Groq (Llama 3.1 70B)** | 30 requests/minute | $0 |
| **Resend** | 3,000 emails/month | $0 |
| **Telegram Bot API** | Unlimited | $0 |
| **Supabase** | 500MB database, 2GB bandwidth | $0 |
| **Vercel** | Hobby projects | $0 |
| **GitHub Actions** | 2,000 minutes/month | $0 |
| **Total** | | **$0** |

**Note:** For personal use (~30 subscribers), you'll stay well within free tier limits.

---

## 🧪 Testing

See [`.sisyphus/notepads/everymorning-mvp/TESTING.md`](.sisyphus/notepads/everymorning-mvp/TESTING.md) for comprehensive integration testing guide.

Quick test:

```bash
cd apps/pipeline

# Test individual modules
uv run python -m src.fetcher      # Fetch papers
uv run python -m src.summarizer   # Generate summaries
uv run python -m src.email_sender # Send test email

# Test full pipeline
uv run python -m src.main
```

---

## 🔧 Customization

### Change Delivery Time

Edit `.github/workflows/daily-digest.yml`:

```yaml
schedule:
  - cron: '0 22 * * *'  # 7 AM KST = 22:00 UTC previous day
```

Use [crontab.guru](https://crontab.guru) to generate cron expressions.

### Adjust Paper Selection

Edit `apps/pipeline/src/fetcher.py`:

```python
FIELDS = ["cs", "physics", "bio", "math"]  # Add/remove fields
limit_per_field = 50  # Papers per field
```

Edit `apps/pipeline/src/scorer.py`:

```python
# Adjust scoring weights
score = (citation_velocity * 0.7) + (influential_citations * 0.3)
```

### Customize Email Template

Edit `apps/pipeline/src/email_sender.py` to modify HTML template.

### Customize Telegram Message

Edit `apps/pipeline/src/telegram_sender.py` to modify message format.

---

## 🐛 Troubleshooting

### No email received?

- Check spam/junk folder
- Verify email in Supabase `subscribers` table
- Check Resend dashboard for delivery status
- Verify `RESEND_API_KEY` in GitHub Secrets

### Telegram bot not responding?

- Send `/start` to your bot first
- Verify `telegram_chat_id` in database
- Check `TELEGRAM_BOT_TOKEN` in GitHub Secrets

### Workflow fails?

- Check Actions tab for error logs
- Verify all 5 GitHub Secrets are set correctly
- Ensure Supabase tables exist
- Check API service status pages

### No papers fetched?

- Semantic Scholar API rate limit (wait 1 hour)
- Check [status.semanticscholar.org](https://status.semanticscholar.org)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[Semantic Scholar](https://www.semanticscholar.org/)** - Free academic paper API
- **[Groq](https://groq.com/)** - Lightning-fast LLM inference
- **[Resend](https://resend.com/)** - Developer-friendly email API
- **[Supabase](https://supabase.com/)** - Open source Firebase alternative

---

## 🚧 Roadmap

- [ ] Web UI for subscriber management
- [ ] Field-specific preferences (e.g., only CS papers)
- [ ] Weekly digest option
- [ ] Paper bookmarking feature
- [ ] RSS feed support

---

## 🤝 Contributing

Contributions welcome! Feel free to:

- Report bugs via GitHub Issues
- Submit pull requests
- Suggest new features
- Improve documentation

---

**Built with ❤️ for researchers, grad students, and STEM enthusiasts.**
