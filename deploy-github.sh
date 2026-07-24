#!/usr/bin/env bash
# Build static site for GitHub Pages (baseurl="") into ../ (repo root), ready to commit.
# Does NOT push. After this, from public_html: git add … && git commit && git push
set -euo pipefail
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
rsync -a \
  --exclude '/academic-website-template/' \
  --exclude '/backup_hyperspace_*/' \
  --exclude '/.git/' \
  --exclude '/.env' \
  --exclude '/data/' \
  "$ROOT/_site/" "$DEST/"

echo "GitHub Pages build is in the repo root. Review, commit, and push master."
echo "Then re-run ./deploy.sh to restore Leiden paths on the local Apache tree."
