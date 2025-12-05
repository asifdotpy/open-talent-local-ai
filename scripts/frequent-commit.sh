#!/usr/bin/env bash
# frequent-commit.sh
# Atomic commit helper for rapid, low-risk development.
# Usage:
#   ./scripts/frequent-commit.sh [path(optional)] ["commit message(optional)"]
# If commit message omitted, uses: "chore: frequent commit <timestamp>"
# If path omitted, stages all modified/removed files (equivalent to -u).
# Handles submodules by committing their changes first if any.

set -euo pipefail

TIMESTAMP="$(date +'%Y-%m-%d %H:%M')"
SCOPE_PATH="${1:-}"
RAW_MSG="${2:-}"
DEFAULT_MSG="chore: frequent commit ${TIMESTAMP}"
COMMIT_MSG="${RAW_MSG:-$DEFAULT_MSG}"

# Detect submodule changes and commit them individually.
commit_submodules() {
  git submodule foreach --quiet '(
    CHANGES=$(git status --porcelain) ;
    if [ -n "$CHANGES" ]; then
      echo "[submodule:$name] committing changes" ;
      git add -A ;
      git commit -m "chore(submodule:$name): frequent commit ${TIMESTAMP}" || true ;
    fi
  )'
}

stage_changes() {
  if [ -n "$SCOPE_PATH" ]; then
    if [ -d "$SCOPE_PATH" ] || [ -f "$SCOPE_PATH" ]; then
      git add "$SCOPE_PATH"
    else
      echo "Path '$SCOPE_PATH' not found; falling back to modified files." >&2
      git add -u
    fi
  else
    git add -u
  fi
}

main() {
  commit_submodules
  stage_changes

  # Abort if nothing staged.
  if [ -z "$(git diff --cached --name-only)" ]; then
    echo "No changes staged; nothing to commit." >&2
    exit 0
  fi

  git commit -m "$COMMIT_MSG" || {
    echo "Commit failed (possibly empty); aborting push." >&2
    exit 1
  }

  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
  echo "Pushing to origin/$CURRENT_BRANCH ..."
  git push origin "$CURRENT_BRANCH"
  echo "Done: $COMMIT_MSG"
}

main "$@"
