#!/usr/bin/env bash
# Make public_html readable by Apache userdir (world-readable pages).
# Safe to run anytime. Keeps secrets private (.env, .git, template, data).
#
# Root cause this fixes: umask 077 → Jekyll/rsync create dirs as 700 and
# files as 600. Apache then cannot traverse publications/ etc. and returns
# "Server unable to read htaccess file" even when no .htaccess exists.
set -euo pipefail

DEST="${1:-}"
if [[ -z "$DEST" ]]; then
  HERE="$(cd "$(dirname "$0")" && pwd)"
  if [[ -f "$HERE/index.html" && -d "$HERE/assets" ]]; then
    DEST="$HERE"
  else
    DEST="$(cd "$HERE/.." && pwd)"
  fi
fi

if [[ ! -d "$DEST" ]]; then
  echo "Destination not found: $DEST" >&2
  exit 1
fi

echo "Fixing web permissions under $DEST ..."

chmod 755 "$DEST"

find "$DEST" \
  \( \
    -path "$DEST/academic-website-template" -o \
    -path "$DEST/academic-website-template/*" -o \
    -path "$DEST/backup_hyperspace_*" -o \
    -path "$DEST/backup_hyperspace_*/*" -o \
    -path "$DEST/.git" -o \
    -path "$DEST/.git/*" -o \
    -path "$DEST/data" -o \
    -path "$DEST/data/*" \
  \) -prune -o \
  -type d -exec chmod 755 {} +

find "$DEST" \
  \( \
    -path "$DEST/academic-website-template" -o \
    -path "$DEST/academic-website-template/*" -o \
    -path "$DEST/backup_hyperspace_*" -o \
    -path "$DEST/backup_hyperspace_*/*" -o \
    -path "$DEST/.git" -o \
    -path "$DEST/.git/*" -o \
    -path "$DEST/data" -o \
    -path "$DEST/data/*" -o \
    -name '.env' \
  \) -prune -o \
  -type f -exec chmod 644 {} +

# Secrets stay private
[[ -f "$DEST/.env" ]] && chmod 600 "$DEST/.env"

# Restore execute bits that the 644 pass above would strip
for f in \
  "$DEST/verify-github-paths.sh" \
  "$DEST/fix-web-perms.sh" \
  "$DEST/install-git-hooks.sh" \
  "$DEST/deploy-github.sh" \
  "$DEST/serve.sh" \
  "$DEST/local_html_site.sh" \
  "$DEST/git-hooks/pre-commit" \
  "$DEST/academic-website-template/deploy.sh" \
  "$DEST/academic-website-template/deploy-github.sh" \
  "$DEST/academic-website-template/fix-web-perms.sh" \
  "$DEST/academic-website-template/verify-github-paths.sh" \
  "$DEST/academic-website-template/install-git-hooks.sh" \
  "$DEST/academic-website-template/serve.sh" \
  "$DEST/.git/hooks/pre-commit"
do
  [[ -f "$f" ]] && chmod 755 "$f"
done

echo "Web permissions OK (dirs 755, files 644; scripts 755; .env kept 600)."
