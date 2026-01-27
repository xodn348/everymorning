# Integration Testing Guide

This guide walks you through manually testing the everymorning daily digest pipeline end-to-end.

## Overview

The pipeline:
1. Fetches recent STEM papers from Semantic Scholar API
2. Scores and selects top 3 papers
3. Generates AI summaries using Groq (Llama 3.1 70B)
4. Sends digest via email (Resend) and Telegram
5. Stores papers in Supabase database

## Prerequisites

Before testing, you need:

### 1. Supabase Project
- Create a free project at [supabase.com](https://supabase.com)
- Get your project URL and anon key from Settings → API
- Create required tables (see Database Schema below)

### 2. Resend Account
- Sign up at [resend.com](https://resend.com) (free tier: 100 emails/day)
- Get API key from Settings → API Keys
- Verify your domain OR use `onboarding@resend.dev` for testing

### 3. Telegram Bot
- Message [@BotFather](https://t.me/botfather) on Telegram
- Create new bot with `/newbot` command
- Save the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 4. Groq API Key
- Sign up at [console.groq.com](https://console.groq.com) (free tier available)
- Create API key from Settings → API Keys

### 5. GitHub Repository
- Fork or clone this repository
- Enable GitHub Actions in Settings → Actions

---

## Database Schema

Create these tables in Supabase SQL Editor:

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

-- Add test subscriber
INSERT INTO subscribers (email, telegram_chat_id, is_active)
VALUES ('your-email@example.com', NULL, TRUE);
```

**Note:** Replace `your-email@example.com` with your actual email for testing.

---

## Step 1: Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions → New repository secret

Add these 5 secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SUPABASE_URL` | Your Supabase project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Your Supabase anon/public key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `GROQ_API_KEY` | Your Groq API key | `gsk_xxxxxxxxxxxxx` |
| `RESEND_API_KEY` | Your Resend API key | `re_xxxxxxxxxxxxx` |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` |

**Important:** 
- Copy-paste carefully - no extra spaces
- Secrets are encrypted and hidden after saving
- You can update them anytime

---

## Step 2: Manual Workflow Trigger

### Option A: GitHub Web UI

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Daily Digest** workflow (left sidebar)
4. Click **Run workflow** button (right side)
5. Select branch (usually `main`)
6. Click green **Run workflow** button

### Option B: GitHub CLI

```bash
gh workflow run daily-digest.yml
```

### What Happens Next

The workflow will:
- ✅ Checkout code
- ✅ Install Python 3.12 and uv
- ✅ Install dependencies
- ✅ Run the pipeline (`uv run python -m src.main`)

Expected runtime: **2-3 minutes**

---

## Step 3: Monitor Workflow Execution

### View Logs

1. Go to Actions tab
2. Click on the running workflow
3. Click on the `digest` job
4. Expand each step to see logs

### Expected Log Output

```
[2026-01-27T...] Starting daily digest pipeline
[2026-01-27T...] Step 1: Fetching papers from all STEM fields
Fetching cs papers...
Fetching physics papers...
Fetching bio papers...
Fetching math papers...
[2026-01-27T...] Fetched 200 papers
[2026-01-27T...] Step 2: Scoring and selecting top 3 papers
[2026-01-27T...] Selected 3 top papers
[2026-01-27T...] Step 3: Generating summaries for top papers
Summarized: ...
[2026-01-27T...] Generated summaries for 3 papers
[2026-01-27T...] Step 4: Fetching subscribers from database
[2026-01-27T...] Retrieved 1 email subscribers and 0 Telegram subscribers
[2026-01-27T...] Step 5: Sending email digest to 1 subscribers
Email sent to your-email@example.com
[2026-01-27T...] Email result: 1/1 sent
[2026-01-27T...] Daily digest pipeline completed successfully
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `SUPABASE_URL must be set` | Missing secret | Add secret in GitHub Settings |
| `401 Unauthorized` | Invalid API key | Check secret value (no spaces) |
| `Table 'papers' does not exist` | Database not set up | Run SQL schema from above |
| `No subscribers found` | Empty subscribers table | Insert test subscriber |
| `Rate limit exceeded` | Too many API calls | Wait 1 hour and retry |

---

## Step 4: Verify Email Delivery

### Check Your Inbox

1. Open your email (the one you added to `subscribers` table)
2. Look for email from `onboarding@resend.dev` (or your verified domain)
3. Subject: **📚 everymorning - Today's Top STEM Papers**

### Expected Email Content

```
📚 everymorning
Daily STEM Paper Digest

#1 [Paper Title]
🎯 TL;DR
[One sentence summary]

💡 Why it matters
[2 sentences about significance]

🔬 Key contribution
• [Contribution 1]
• [Contribution 2]

Read paper → [Link]

[Repeat for papers #2 and #3]
```

### Troubleshooting

- **No email received?**
  - Check spam/junk folder
  - Verify email in Supabase `subscribers` table
  - Check Resend dashboard for delivery status
  - Verify `RESEND_API_KEY` is correct

- **Email looks broken?**
  - HTML rendering issue - try different email client
  - Check workflow logs for errors

---

## Step 5: Verify Telegram Delivery

### Subscribe to Bot

1. Open Telegram
2. Search for your bot (the name you gave to @BotFather)
3. Start a chat with `/start`
4. Get your chat ID:
   ```bash
   # Use Telegram Bot API
   curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
5. Add your chat ID to Supabase:
   ```sql
   UPDATE subscribers 
   SET telegram_chat_id = YOUR_CHAT_ID 
   WHERE email = 'your-email@example.com';
   ```

### Re-run Workflow

Trigger the workflow again (Step 2) to test Telegram delivery.

### Expected Telegram Message

```
📚 everymorning - Daily STEM Paper Digest

#1 [Paper Title]

🎯 TL;DR
[Summary]

💡 Why it matters
[Significance]

🔬 Key contribution
• [Contribution 1]
• [Contribution 2]

Read paper → [Link]

---

[Papers #2 and #3]
```

### Troubleshooting

- **No message received?**
  - Verify `telegram_chat_id` in database
  - Check bot token is correct
  - Ensure you started the bot (`/start`)
  - Check workflow logs for errors

---

## Step 6: Verify Supabase Data

### Check Papers Table

1. Go to Supabase Dashboard → Table Editor
2. Select `papers` table
3. You should see ~200 papers inserted

### Verify Data

```sql
-- Count papers
SELECT COUNT(*) FROM papers;

-- View recent papers
SELECT title, score, published_at 
FROM papers 
ORDER BY score DESC 
LIMIT 10;

-- Check for duplicates (should be 0)
SELECT external_id, COUNT(*) 
FROM papers 
GROUP BY external_id 
HAVING COUNT(*) > 1;
```

### Expected Results

- **Total papers:** ~200 (50 per field × 4 fields)
- **Top scores:** 0.5 - 2.0 range
- **No duplicates:** Unique constraint on `(source, external_id)`

---

## Step 7: Test Scheduled Run (Optional)

The workflow runs automatically at **7 AM KST (10 PM UTC previous day)**.

To verify:
1. Wait for scheduled time
2. Check Actions tab for automatic run
3. Verify email/Telegram delivery

**Note:** You can disable scheduled runs in `.github/workflows/daily-digest.yml` by commenting out the `schedule` section.

---

## Success Criteria

✅ **All checks must pass:**

- [ ] Workflow runs without errors
- [ ] Email received with 3 papers
- [ ] Telegram message received (if configured)
- [ ] ~200 papers saved in Supabase
- [ ] No duplicate papers in database
- [ ] Summaries are coherent and well-formatted
- [ ] Links in email/Telegram work correctly

---

## Common Issues & Solutions

### Issue: "No papers fetched"

**Cause:** Semantic Scholar API rate limit or network issue

**Solution:**
- Wait 1 hour and retry
- Check Semantic Scholar API status
- Reduce `limit_per_field` in `fetcher.py`

### Issue: "Groq API error"

**Cause:** Invalid API key or rate limit

**Solution:**
- Verify `GROQ_API_KEY` in GitHub Secrets
- Check Groq dashboard for quota
- Free tier: 30 requests/minute

### Issue: "Resend 401 Unauthorized"

**Cause:** Invalid API key

**Solution:**
- Regenerate API key in Resend dashboard
- Update `RESEND_API_KEY` secret
- Ensure no extra spaces in secret

### Issue: "Telegram bot not responding"

**Cause:** Bot token invalid or bot not started

**Solution:**
- Verify token with @BotFather
- Send `/start` to your bot
- Check bot privacy settings

### Issue: "Supabase connection failed"

**Cause:** Wrong URL or key

**Solution:**
- Copy URL/key from Supabase Settings → API
- Ensure using `anon` key, not `service_role` key
- Check project is not paused (free tier)

---

## Advanced Testing

### Test Individual Modules

```bash
cd apps/pipeline

# Test fetcher
uv run python -m src.fetcher

# Test scorer
uv run python -c "from src.scorer import calculate_score; print(calculate_score({'citationCount': 50, 'influentialCitationCount': 10, 'publicationDate': '2026-01-15'}))"

# Test summarizer
uv run python -m src.summarizer

# Test email sender
uv run python -m src.email_sender

# Test telegram sender
uv run python -m src.telegram_sender
```

### Local Testing

```bash
# Copy .env.example to .env
cp .env.example .env

# Fill in your API keys
nano .env

# Run pipeline locally
cd apps/pipeline
uv run python -m src.main
```

---

## Performance Benchmarks

Expected performance on GitHub Actions (ubuntu-latest):

| Step | Duration | Notes |
|------|----------|-------|
| Fetch papers | 30-60s | 4 API calls with 1s delay |
| Score papers | <1s | Pure computation |
| Generate summaries | 10-20s | 3 Groq API calls |
| Send emails | 5-10s | Depends on recipient count |
| Send Telegram | 2-5s | Depends on recipient count |
| **Total** | **2-3 min** | End-to-end |

---

## Next Steps

After successful testing:

1. **Add more subscribers** to Supabase `subscribers` table
2. **Customize email template** in `email_sender.py`
3. **Adjust scoring weights** in `scorer.py`
4. **Change schedule** in `.github/workflows/daily-digest.yml`
5. **Monitor costs** (all services have free tiers)

---

## Support

If you encounter issues:

1. Check workflow logs in GitHub Actions
2. Review this troubleshooting guide
3. Verify all secrets are set correctly
4. Test individual modules locally
5. Check API service status pages

---

## API Service Status Pages

- Semantic Scholar: [status.semanticscholar.org](https://status.semanticscholar.org)
- Groq: [status.groq.com](https://status.groq.com)
- Resend: [status.resend.com](https://status.resend.com)
- Telegram: [telegram.org/status](https://telegram.org/status)
- Supabase: [status.supabase.com](https://status.supabase.com)

---

**Last Updated:** 2026-01-27
