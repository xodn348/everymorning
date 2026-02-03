# stemem.info Domain Setup Guide

## ✅ Completed
- [x] Vercel domain added: stemem.info
- [x] Vercel domain added: www.stemem.info
- [x] Email sender updated: fresh@stemem.info

## 🔧 Manual Steps Required

### Step 1: Add DNS Records in Porkbun

Go to: https://porkbun.com/account/domainsSpeedo

**For stemem.info domain, add these records:**

#### 1. A Record (Root Domain)
```
Type:   A
Host:   @ (or leave blank for root)
Answer: 76.76.21.21
TTL:    600 (default)
```

#### 2. A Record (WWW Subdomain)
```
Type:   A
Host:   www
Answer: 76.76.21.21
TTL:    600 (default)
```

### Existing Email Records (DO NOT DELETE)
These should already exist from previous setup:

```
Type: TXT
Host: resend._domainkey
Answer: p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDGRlP+...

Type: MX
Host: send
Answer: feedback-smtp.us-east-1.amazonses.com
Priority: 10

Type: TXT  
Host: send
Answer: v=spf1 include:amazonses.com ~all
```

### Step 2: Wait for DNS Propagation

DNS changes can take 5 minutes to 48 hours. Usually it's quick (5-15 minutes).

Check propagation status:
```bash
# Check A record
dig stemem.info A +short
# Should show: 76.76.21.21

# Check www
dig www.stemem.info A +short  
# Should show: 76.76.21.21
```

Or use online tool: https://dnschecker.org/#A/stemem.info

### Step 3: Verify in Vercel

Once DNS propagates, Vercel will automatically verify and issue SSL certificate.

Check status:
```bash
cd "/Users/jnnj92/Desktop/1. TAMU/00. Ebsilon/everymorning/apps/web"
vercel domains inspect stemem.info
```

Expected output after verification:
```
✓ Domain stemem.info is configured properly
✓ SSL certificate issued
```

### Step 4: Test the Site

After verification completes:
- Visit: https://stemem.info
- Visit: https://www.stemem.info

Both should show the everymorning landing page.

---

## Summary of Changes

| Item | Before | After |
|------|--------|-------|
| Website | everymorning.vercel.app | stemem.info |
| Email sender | newsletter@stemem.info | fresh@stemem.info |
| DNS Records | MX, TXT (email only) | + A records (web + email) |

## Troubleshooting

**Q: Domain shows "Parked on the Bun" after 24 hours**  
A: Double-check A records are set to `76.76.21.21`, not Porkbun's parking IP.

**Q: Certificate error in browser**  
A: Wait for Vercel to issue SSL cert (usually 5-10 min after DNS verification).

**Q: Emails stopped working**  
A: Make sure you didn't delete the existing MX/TXT records for email.

---

**Next Step**: Add the A records in Porkbun dashboard, then wait 5-15 minutes.
