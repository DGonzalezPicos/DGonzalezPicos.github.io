#!/usr/bin/env bash
# Fail if the working tree looks like a Leiden-only build (baseurl=/~picos).
# GitHub Pages is served from the domain root, so /~picos/assets/* 404s.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
if [[ -f "$HERE/index.html" && -d "$HERE/assets" ]]; then
  ROOT="$HERE"
elif [[ -f "$HERE/../index.html" ]]; then
  ROOT="$(cd "$HERE/.." && pwd)"
else
  echo "ERROR: cannot locate site root from $HERE" >&2
  exit 1
fi
cd "$ROOT"

mapfile -t bad < <(
  find . -type f \( -name '*.html' -o -name 'feed.xml' -o -name 'sitemap.xml' -o -name 'search.json' \) \
    ! -path './academic-website-template/*' \
    ! -path './backup_hyperspace_*/*' \
    ! -path './backup_jekyll_*/*' \
    ! -path './.git/*' \
    ! -path './data/*' \
    -print0 | xargs -0 grep -l '/~picos/' 2>/dev/null || true
)

if ((${#bad[@]})); then
  echo "ERROR: Leiden paths (/~picos/) found in files destined for GitHub Pages:" >&2
  printf '  %s\n' "${bad[@]}" >&2
  echo >&2
  echo "Use relative asset paths (assets/..., images/..., papers/...) so both" >&2
  echo "GitHub Pages and Leiden /~picos/ resolve correctly." >&2
  exit 1
fi

if ! grep -Eq 'href="(\./)?assets/site\.css"|href="/assets/site\.css"' index.html 2>/dev/null; then
  echo "ERROR: index.html does not reference assets/site.css (GitHub-safe paths)." >&2
  echo "Current stylesheet lines:" >&2
  grep -n 'stylesheet\|site.css\|main.css' index.html >&2 || true
  exit 1
fi

echo "GitHub Pages path check OK (no /~picos/; assets/site.css present)."
