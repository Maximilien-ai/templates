#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

CI_MODE="${1:-}"
TOOLS_DIR="$ROOT_DIR/.tools"
VENV_DIR="$TOOLS_DIR/venv"
NODE_BIN="$TOOLS_DIR/node_modules/.bin/markdownlint-cli2"
LOCAL_BIN_DIR="$TOOLS_DIR/bin"

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
mkdir -p "$TOOLS_DIR" "$LOCAL_BIN_DIR"

if [[ ! -x "$NODE_BIN" ]]; then
  echo "Installing markdownlint-cli2..."
  npm install --prefix "$TOOLS_DIR" markdownlint-cli2
fi

if [[ ! -x "$VENV_DIR/bin/ruff" ]]; then
  echo "Installing ruff..."
  python3 -m venv "$VENV_DIR"
  "$VENV_DIR/bin/python" -m pip install --upgrade pip
  "$VENV_DIR/bin/pip" install ruff
fi

if [[ ! -x "$LOCAL_BIN_DIR/actionlint" ]] && ! command -v actionlint >/dev/null 2>&1; then
  echo "Installing actionlint..."
  if command -v go >/dev/null 2>&1; then
    GOBIN="$LOCAL_BIN_DIR" go install github.com/rhysd/actionlint/cmd/actionlint@latest
  elif [[ "$CI_MODE" != "--ci" ]] && command -v brew >/dev/null 2>&1; then
    brew install actionlint
  else
    echo "Unable to auto-install actionlint. Install Go or Homebrew and rerun ./setup.sh." >&2
    exit 1
  fi
fi

echo "Setup complete."
