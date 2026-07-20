#!/bin/bash
# Run this once to commit the repo and push it to GitHub.
# Requires: git, gh (GitHub CLI) — install gh with: brew install gh
# Then authenticate with: gh auth login

set -e

cd "$(dirname "$0")"

echo "=== ai-video-dev: initial GitHub push ==="

# Clean up any stale git lock files
rm -f .git/index.lock 2>/dev/null || true

# Configure git if not already set
git config user.email "manoj@misalabs.ai" 2>/dev/null || true
git config user.name "Manoj Elango" 2>/dev/null || true

# Init if not already a git repo
if [ ! -d .git ]; then
  git init
  git branch -m main
fi

# Stage and commit
git add .
git commit -m "Initial commit: ai-video-dev v0.1.0

- CLI with analyze, grade, compile, audio, overlay, end-card, pipeline commands
- 8 battle-tested color grade presets (ffmpeg filter chains)
- Claude API integration for AI-powered grade recommendations
- ProRes vertical pipeline optimized for iPhone footage
- Full documentation and setup guide
- Contributing guide for community grade submissions" || echo "(nothing new to commit)"

# Create public GitHub repo and push
echo ""
echo "Creating public GitHub repo: ai-video-dev..."
gh repo create ai-video-dev \
  --public \
  --description "AI-first video editing pipeline powered by ffmpeg + Claude" \
  --push \
  --source . \
  --remote origin

echo ""
echo "Done! Your repo is live at: https://github.com/manojelango/ai-video-dev"
