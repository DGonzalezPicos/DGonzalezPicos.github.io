#!/usr/bin/env bash
# Preferred local preview: Jekyll serve (live reload, correct baseurl).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ -x /home/picos/.local/bin/micromamba ]]; then
  export MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-/data2/picos/.local/micromamba}"
  eval "$(/home/picos/.local/bin/micromamba shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX")"
  micromamba activate jekyll
fi

PORT="${1:-4000}"
echo "Open: http://localhost:${PORT}/~picos/"
exec bundle exec jekyll serve --host 127.0.0.1 --port "$PORT" --livereload
