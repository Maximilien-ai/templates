#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

CI_MODE="${1:-}"

require_cmd() {
  local cmd="$1"
  local hint="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "$cmd is required. $hint" >&2
    exit 1
  fi
}

require_cmd python3 "Install Python 3.12+."
require_cmd npm "Install Node.js and npm."

if ! command -v markdownlint-cli2 >/dev/null 2>&1; then
  echo "Installing markdownlint-cli2..."
  npm install --global markdownlint-cli2
fi

if ! command -v ruff >/dev/null 2>&1; then
  echo "Installing ruff..."
  if [[ "$CI_MODE" == "--ci" ]]; then
    python3 -m pip install --upgrade pip
    python3 -m pip install ruff
  else
    python3 -m pip install --user ruff
  fi
fi

if ! command -v actionlint >/dev/null 2>&1; then
  echo "Installing actionlint..."
  if command -v brew >/dev/null 2>&1; then
    brew install actionlint
  elif command -v go >/dev/null 2>&1; then
    go install github.com/rhysd/actionlint/cmd/actionlint@latest
    export PATH="$PATH:$HOME/go/bin"
  else
    echo "Skipping actionlint install. Install Homebrew or Go to enable it locally." >&2
  fi
fi

echo "Setup complete."
