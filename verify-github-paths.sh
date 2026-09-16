#!/usr/bin/env bash
# Fail if the working tree looks like a Leiden build (baseurl=/~picos).
# GitHub Pages is served from the domain root, so /~picos/assets/* 404s and
# the site renders unstyled — this has bitten us repeatedly.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
if [[ -f "$HERE/index.html" && -d "$HERE/assets" ]]; then
  ROOT="$HERE"                    # repo root (public_html)
elif [[ -f "$HERE/../index.html" ]]; then
  ROOT="$(cd "$HERE/.." && pwd)"  # called from academic-website-template/
else
  echo "ERROR: cannot locate site root from $HERE" >&2
  exit 1
fi
cd "$ROOT"

mapfile -t bad < <(
  find . -type f \( -name '*.html' -o -name 'feed.xml' -o -name 'sitemap.xml' -o -name 'search.json' \) \
    ! -path './academic-website-template/*' \
    ! -path './backup_hyperspace_*/*' \
    ! -path './.git/*' \
    ! -path './data/*' \
    -print0 | xargs -0 grep -l '/~picos/' 2>/dev/null || true
)

if ((${#bad[@]})); then
  echo "ERROR: Leiden paths (/~picos/) found in files destined for GitHub Pages:" >&2
  printf '  %s\n' "${bad[@]}" >&2
  echo >&2
  echo "Fix:  cd academic-website-template && ./deploy-github.sh" >&2
  echo "Then commit/push, and run ./deploy.sh to restore the Leiden site." >&2
  exit 1
fi

if ! grep -q 'href="/assets/main.css"' index.html 2>/dev/null; then
  echo "ERROR: index.html does not reference /assets/main.css (GitHub root paths)." >&2
  echo "Current stylesheet lines:" >&2
  grep -n 'stylesheet\|main.css' index.html >&2 || true
  echo "Fix:  cd academic-website-template && ./deploy-github.sh" >&2
  exit 1
fi

echo "GitHub Pages path check OK (no /~picos/; /assets/main.css present)."
