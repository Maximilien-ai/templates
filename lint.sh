#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ -x "$ROOT_DIR/node_modules/.bin/markdownlint-cli2" ]]; then
  "$ROOT_DIR/node_modules/.bin/markdownlint-cli2" "**/*.md"
elif command -v markdownlint-cli2 >/dev/null 2>&1; then
  markdownlint-cli2 "**/*.md"
elif command -v npx >/dev/null 2>&1; then
  npx --yes markdownlint-cli2 "**/*.md"
else
  echo "markdownlint-cli2 is required. Install it globally or make npx available." >&2
  exit 1
fi

python3 -m py_compile scripts/*.py

if [[ -x "$ROOT_DIR/.tools/venv/bin/ruff" ]]; then
  "$ROOT_DIR/.tools/venv/bin/ruff" check scripts
elif command -v ruff >/dev/null 2>&1; then
  ruff check scripts
else
  echo "ruff is required. Run ./setup.sh first." >&2
  exit 1
fi

if [[ -x "$ROOT_DIR/.tools/bin/actionlint" ]]; then
  "$ROOT_DIR/.tools/bin/actionlint"
elif command -v actionlint >/dev/null 2>&1; then
  actionlint
else
  echo "actionlint is required. Run ./setup.sh first." >&2
  exit 1
fi
