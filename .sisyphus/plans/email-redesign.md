# Email Template Redesign - Minimal Morning Digest

**STATUS**: ✅ COMPLETE (2026-01-28)

## TL;DR

> **Quick Summary**: 이메일 템플릿을 미니멀하고 모던하게 재디자인. 이모지 제거, 2줄 요약, 링크 포함.
> 
> **Deliverables**:
> - `apps/pipeline/src/email_sender.py` 수정
> - `apps/pipeline/src/summarizer.py` 요약 길이 조정
> 
> **Estimated Effort**: Quick (30분)
> **Parallel Execution**: NO

---

## User Requirements

1. **No emojis** - 이모지 제거, 깔끔하게
2. **Minimalist design** - 모던하고 가벼운 느낌
3. **2줄 요약** - 아침에 빠르게 읽을 수 있게
4. **링크 포함** - 관심있는 사람만 원문 읽도록

---

## Design Decisions

### Color Palette (Monochrome + Accent)
- Background: `#f9fafb` (light gray)
- Card: `#ffffff` (white)
- Text: `#111827` (near-black)
- Secondary: `#6b7280` (gray)
- Link: `#2563eb` (blue accent)
- Border: `#e5e7eb` (light border)

### Typography
- Font: System stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`)
- Body: 16px, line-height 1.6
- Title: 14px, font-weight 600
- Summary: 15px, color #4b5563

### Layout
- Max-width: 520px (narrower = more readable)
- Padding: 32px
- Card spacing: 24px

---

## TODOs

### Task 1: Update email_sender.py - New Minimal Template

**What to do**:
- Replace `format_email_html()` function with minimal design
- Remove all emojis from template
- Simpler card-based layout
- Paper title as link (not separate "Read paper" link)
- Summary limited to 2 lines with CSS

**Must NOT do**:
- Heavy graphics or images
- Multiple colors
- Complex nested tables

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: []

**New HTML Template**:
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light dark">
</head>
<body style="margin: 0; padding: 0; background-color: #f9fafb; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding: 40px 20px;">
    <tr>
      <td align="center">
        <table width="520" cellpadding="0" cellspacing="0" style="max-width: 520px; width: 100%;">
          
          <!-- Header -->
          <tr>
            <td style="padding-bottom: 32px;">
              <h1 style="margin: 0; font-size: 20px; font-weight: 600; color: #111827;">
                everymorning
              </h1>
              <p style="margin: 4px 0 0 0; font-size: 13px; color: #6b7280;">
                Daily STEM Paper Digest
              </p>
            </td>
          </tr>
          
          <!-- Papers -->
          {papers_html}
          
          <!-- Footer -->
          <tr>
            <td style="padding-top: 32px; border-top: 1px solid #e5e7eb;">
              <p style="margin: 0; font-size: 12px; color: #9ca3af; text-align: center;">
                Unsubscribe · everymorning
              </p>
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
```

**Paper Card Template**:
```html
<tr>
  <td style="padding: 20px; background: #ffffff; border-radius: 8px; margin-bottom: 16px;">
    <a href="{url}" style="text-decoration: none;">
      <h2 style="margin: 0 0 8px 0; font-size: 15px; font-weight: 600; color: #111827; line-height: 1.4;">
        {title}
      </h2>
    </a>
    <p style="margin: 0; font-size: 14px; color: #4b5563; line-height: 1.5;">
      {summary}
    </p>
  </td>
</tr>
<tr><td style="height: 12px;"></td></tr>
```

**Acceptance Criteria**:
- [x] No emojis in email
- [x] Clean, minimal design
- [x] Paper title is clickable link
- [x] Summary is 2 lines max
- [x] Mobile-friendly (520px max-width)

**Commit**: YES
- Message: `style(email): redesign to minimal morning digest template`

---

### Task 2: Update summarizer.py - Shorter Summaries

**What to do**:
- Change prompt to generate 1-2 sentence summary only
- Remove structured format (TL;DR, Why it matters, etc.)
- Just one concise paragraph

**Must NOT do**:
- Keep emoji headers
- Keep long multi-section format

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: []

**New Prompt**:
```python
prompt = f"""Summarize this paper in 1-2 sentences. Be concise and technical.
Focus on: What did they do? Why does it matter?
Target audience: researchers who want a quick morning read.

Title: {title}
Abstract: {abstract}

Write only the summary, no headers or formatting."""
```

**Acceptance Criteria**:
- [x] Summary is 1-2 sentences
- [x] No emojis or special formatting
- [x] Plain text output

**Commit**: YES
- Message: `refactor(summarizer): simplify to 2-line summaries`

---

## Success Criteria

```bash
# Test email
cd apps/pipeline
uv run python -c "from src.email_sender import send_digest_email; ..."
# Expected: Clean, minimal email with no emojis
```

### Final Checklist
- [x] No emojis anywhere
- [x] Minimal, modern design
- [x] 2-line summaries
- [x] Title links to paper
- [x] Mobile-friendly

---

## Commit Strategy

| After Task | Message |
|------------|---------|
| 1 | `style(email): redesign to minimal morning digest template` |
| 2 | `refactor(summarizer): simplify to 2-line summaries` |
