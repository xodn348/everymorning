#!/bin/bash
set -e

echo "=== Vercel Domain Setup for stemem.info ==="
echo ""

# Check if logged in
if ! vercel whoami &>/dev/null; then
    echo "Step 1: Logging in to Vercel..."
    vercel login
else
    echo "✓ Already logged in to Vercel"
fi

echo ""
echo "Step 2: Linking project..."
cd apps/web
if [ ! -d ".vercel" ]; then
    vercel link --yes
else
    echo "✓ Project already linked"
fi

echo ""
echo "Step 3: Adding domain stemem.info..."
vercel domains add stemem.info

echo ""
echo "Step 4: Adding domain www.stemem.info..."
vercel domains add www.stemem.info || true

echo ""
echo "=== NEXT STEPS ==="
echo "Vercel will show you DNS records to add in Porkbun."
echo "You need to add these records:"
echo ""
echo "1. A record:"
echo "   Type: A"
echo "   Host: @ (or leave blank)"
echo "   Answer: 76.76.21.21"
echo ""
echo "2. CNAME record for www:"
echo "   Type: CNAME"
echo "   Host: www"
echo "   Answer: cname.vercel-dns.com"
echo ""
echo "After adding DNS records, run:"
echo "  vercel domains inspect stemem.info"
