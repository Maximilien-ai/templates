#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ -x "$ROOT_DIR/node_modules/.bin/prettier" ]]; then
  "$ROOT_DIR/node_modules/.bin/prettier" --write "README.md" "spec/**/*.md" "templates/**/*.md" "docs/**/*.md" ".github/**/*.md"
elif command -v prettier >/dev/null 2>&1; then
  prettier --write "README.md" "spec/**/*.md" "templates/**/*.md" "docs/**/*.md" ".github/**/*.md"
elif command -v npx >/dev/null 2>&1; then
  npx --yes prettier --write "README.md" "spec/**/*.md" "templates/**/*.md" "docs/**/*.md" ".github/**/*.md"
else
  echo "prettier is required. Run ./setup.sh first." >&2
  exit 1
fi

if [[ -x "$ROOT_DIR/node_modules/.bin/markdownlint-cli2" ]]; then
  "$ROOT_DIR/node_modules/.bin/markdownlint-cli2" --fix "README.md" "spec/**/*.md" "templates/**/*.md" "docs/**/*.md" ".github/**/*.md"
elif command -v markdownlint-cli2 >/dev/null 2>&1; then
  markdownlint-cli2 --fix "README.md" "spec/**/*.md" "templates/**/*.md" "docs/**/*.md" ".github/**/*.md"
elif command -v npx >/dev/null 2>&1; then
  npx --yes markdownlint-cli2 --fix "README.md" "spec/**/*.md" "templates/**/*.md" "docs/**/*.md" ".github/**/*.md"
else
  echo "markdownlint-cli2 is required. Run ./setup.sh first." >&2
  exit 1
fi
