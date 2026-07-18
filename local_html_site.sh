#!/usr/bin/env bash
# Local preview for the deployed site (baseurl=/~picos).
# Plain `python3 -m http.server` from public_html fails because CSS/JS
# are requested as /~picos/assets/... — this script mirrors that path.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PORT="${1:-8008}"
STAGING="${TMPDIR:-/tmp}/picos_site_preview_$$"

mkdir -p "$STAGING"
# Literal "~picos" directory name so GET /~picos/assets/... resolves
ln -sfn "$ROOT" "$STAGING/~picos"

cleanup() { rm -rf "$STAGING"; }
trap cleanup EXIT

echo "Serving $ROOT"
echo "Open:  http://localhost:${PORT}/~picos/"
echo "(Ctrl+C to stop)"
cd "$STAGING"
exec python3 -m http.server "$PORT"
