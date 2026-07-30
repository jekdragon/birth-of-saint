#!/bin/bash
# Deploy to GitHub Pages
# Usage: bash deploy_ghpages.sh <repo-name>

set -e

REPO=${1:-birth-of-saint}
echo "=== Deploying $REPO to GitHub Pages ==="

# 1. Build with pygbag
echo "[1/4] Building with pygbag..."
python -m pygbag --build .

# 2. Copy index.html to build/web/
echo "[2/4] Copying index.html..."
cp index.html build/web/index.html

# 3. Create gh-pages branch
echo "[3/4] Creating gh-pages branch..."
git subtree split --prefix build/web -b gh-pages 2>/dev/null || {
    echo "Creating fresh gh-pages branch..."
    git checkout --orphan gh-pages
    git rm -rf .
    cp -r build/web/* .
    git add .
    git commit -m "Deploy: $REPO web build"
    git checkout main
}

# 4. Push to GitHub
echo "[4/4] Pushing to GitHub..."
git push origin gh-pages --force

echo ""
echo "=== Done! ==="
echo "Your game will be available at:"
echo "  https://<your-username>.github.io/$REPO/"
echo ""
echo "Don't forget to:"
echo "  1. Create repo on GitHub: gh repo create $REPO --public"
echo "  2. Enable GitHub Pages in repo settings (source: gh-pages branch)"
echo "  3. Upload to itch.io: zip the build/web/ folder"
