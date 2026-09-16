#!/usr/bin/env bash
# Install repo hooks that prevent committing Leiden paths to GitHub Pages.
set -euo pipefail
TEMPLATE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$TEMPLATE/.." && pwd)"

mkdir -p "$REPO/.git/hooks"
cp "$TEMPLATE/git-hooks/pre-commit" "$REPO/.git/hooks/pre-commit"
chmod 755 "$REPO/.git/hooks/pre-commit"

# Keep a non-ignored copy of the verifier at repo root (template dir is gitignored)
cp "$TEMPLATE/verify-github-paths.sh" "$REPO/verify-github-paths.sh"
chmod 755 "$REPO/verify-github-paths.sh"

echo "Installed $REPO/.git/hooks/pre-commit"
echo "Installed $REPO/verify-github-paths.sh"
