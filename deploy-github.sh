#!/usr/bin/env bash
# Build static site for GitHub Pages (baseurl="") into ../ (repo root), ready to commit.
# Does NOT push. After this, from public_html: git add … && git commit && git push
#
# IMPORTANT: This overwrites Leiden (/~picos) paths with GitHub (/) paths in the
# shared public_html tree. After pushing to GitHub, always run ./deploy.sh so the
# local Apache site works again — and so web permissions stay Apache-readable.
set -euo pipefail

umask 022

ROOT="$(cd "$(dirname "$0")" && pwd)"
DEST="$(dirname "$ROOT")"
cd "$ROOT"

if [[ -x /home/picos/.local/bin/micromamba ]]; then
  export MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-/data2/picos/.local/micromamba}"
  eval "$(/home/picos/.local/bin/micromamba shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX")"
  micromamba activate jekyll
fi

echo "Building for GitHub Pages (baseurl='')..."
bundle exec jekyll build --config _config.yml

echo "Syncing _site → $DEST (excluding source/backup/secrets)..."
rsync -a --chmod=D755,F644 \
  --exclude '/academic-website-template/' \
  --exclude '/backup_hyperspace_*/' \
  --exclude '/.git/' \
  --exclude '/.env' \
  --exclude '/data/' \
  "$ROOT/_site/" "$DEST/"

# Keep the shared tree Apache-readable even though URLs are GitHub-shaped for now
"$ROOT/fix-web-perms.sh" "$DEST"

# Guardrail: refuse to leave a Leiden-shaped tree ready for an accidental commit
"$ROOT/verify-github-paths.sh"

echo "GitHub Pages build is in the repo root. Review, commit, and push master."
echo "Then re-run ./deploy.sh to restore Leiden paths (/~picos) on the local Apache tree."
