#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh is required to apply branch protection." >&2
  exit 1
fi

REMOTE_URL="$(git remote get-url origin)"
REPO_SLUG="$(printf '%s\n' "$REMOTE_URL" | sed -E 's#(git@github.com:|https://github.com/)##; s#\.git$##')"

if [[ -z "$REPO_SLUG" ]]; then
  echo "Unable to determine repository slug from origin remote." >&2
  exit 1
fi

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "repos/$REPO_SLUG/branches/main/protection" \
  --input .github/branch-protection-main.json

echo "Applied branch protection to main for $REPO_SLUG."
