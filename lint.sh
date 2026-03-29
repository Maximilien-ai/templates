#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if command -v markdownlint-cli2 >/dev/null 2>&1; then
  markdownlint-cli2 "**/*.md"
elif command -v npx >/dev/null 2>&1; then
  npx --yes markdownlint-cli2 "**/*.md"
else
  echo "markdownlint-cli2 is required. Install it globally or make npx available." >&2
  exit 1
fi

python3 -m py_compile scripts/*.py

if command -v ruff >/dev/null 2>&1; then
  ruff check scripts
else
  echo "ruff not installed; skipping Python style lint." >&2
fi

if command -v actionlint >/dev/null 2>&1; then
  actionlint
else
  echo "actionlint not installed; skipping GitHub Actions lint." >&2
fi
