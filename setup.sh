#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

CI_MODE="${1:-}"
TOOLS_DIR="$ROOT_DIR/.tools"
VENV_DIR="$TOOLS_DIR/venv"
NODE_BIN="$ROOT_DIR/node_modules/.bin/markdownlint-cli2"
LOCAL_BIN_DIR="$TOOLS_DIR/bin"
RUFF_VERSION="$(awk -F'==' '/^ruff==/ { print $2 }' requirements-dev.txt)"

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

if [[ ! -x "$NODE_BIN" ]] || ! npm ls --depth=0 >/dev/null 2>&1; then
  echo "Installing Node-based repo tools..."
  npm install
fi

if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi

if [[ ! -x "$VENV_DIR/bin/ruff" ]] || [[ "$("$VENV_DIR/bin/ruff" --version | awk '{ print $2 }')" != "$RUFF_VERSION" ]]; then
  echo "Installing ruff..."
  "$VENV_DIR/bin/python" -m pip install --upgrade pip
  "$VENV_DIR/bin/pip" install -r requirements-dev.txt
fi

if [[ ! -x "$LOCAL_BIN_DIR/actionlint" ]] && ! command -v actionlint >/dev/null 2>&1; then
  echo "Installing actionlint..."
  if command -v go >/dev/null 2>&1; then
      if ! GOBIN="$LOCAL_BIN_DIR" go install github.com/rhysd/actionlint/cmd/actionlint@latest; then
        if [[ "$CI_MODE" != "--ci" ]] && command -v brew >/dev/null 2>&1; then
          echo "Falling back to Homebrew for actionlint..."
          brew install actionlint
        else
          echo "Unable to auto-install actionlint. The current actionlint release requires Go 1.25+." >&2
          echo "Upgrade Go to 1.25+, install actionlint manually, or rerun ./setup.sh on a machine with Homebrew." >&2
          exit 1
        fi
      fi
  elif [[ "$CI_MODE" != "--ci" ]] && command -v brew >/dev/null 2>&1; then
    brew install actionlint
  else
    echo "Unable to auto-install actionlint. Install Go 1.25+ or Homebrew and rerun ./setup.sh." >&2
    exit 1
  fi
fi

echo "Setup complete."
