#!/usr/bin/env bash
set -euo pipefail

# sync_notebook.sh
# Simple helper to copy a notebook from the repo to a destination (Windows Desktop, Drive, etc.)
# Optional: create a git commit & push or copy via rclone

usage() {
  cat <<EOF
Usage: $0 --src <source-notebook> --dest <destination-path> [--branch <branch>] [--git] [--rclone <remote:path>]

Options:
  --src        Path to source notebook (relative or absolute)
  --dest       Destination path (file or directory)
  --branch     Git branch to push to (default: feat/sync-notebooks)
  --git        If provided, will git add/commit/push the notebook to the repo (creates branch if needed)
  --rclone     If provided, will run: rclone copy <dest> <remote:path>
  -h|--help    Show this help

Examples:
  # Copy to Windows OneDrive Desktop (WSL):
  $0 --src notebooks/granite_fine_tuning_colab.ipynb --dest /mnt/c/Users/asif1/OneDrive/Desktop/

  # Copy to regular Windows Desktop (WSL):
  $0 --src notebooks/granite_fine_tuning_colab.ipynb --dest /mnt/c/Users/asif1/Desktop/

  # Copy to /tmp for testing:
  $0 --src notebooks/granite_fine_tuning_colab.ipynb --dest /tmp/granite_test.ipynb

EOF
}

SRC=""
DEST=""
BRANCH="feat/sync-notebooks"
DO_GIT=0
RCLONE_DEST=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --src) SRC="$2"; shift 2 ;;
    --dest) DEST="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    --git) DO_GIT=1; shift ;;
    --rclone) RCLONE_DEST="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

if [[ -z "$SRC" || -z "$DEST" ]]; then
  echo "ERROR: --src and --dest are required"
  usage
  exit 2
fi

if [[ ! -f "$SRC" ]]; then
  echo "ERROR: source file not found: $SRC"
  exit 3
fi

# If dest is a directory, place file inside it
if [[ -d "$DEST" ]]; then
  BASENAME=$(basename "$SRC")
  DEST_PATH="$DEST/$BASENAME"
else
  DEST_PATH="$DEST"
fi

echo "Copying $SRC -> $DEST_PATH"
cp -v "$SRC" "$DEST_PATH"

if [[ $DO_GIT -eq 1 ]]; then
  # Ensure we're inside repo root (assume script run from repo root)
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Preparing git branch $BRANCH"
    git fetch origin || true
    if ! git show-ref --verify --quiet refs/heads/$BRANCH; then
      git checkout -b "$BRANCH"
    else
      git checkout "$BRANCH"
    fi

    git add "$DEST_PATH"
    TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    git commit -m "chore(sync): add/update notebook $BASENAME ($TS)" || echo "No changes to commit"
    git push -u origin "$BRANCH"
  else
    echo "Not a git repo, skipping git step"
  fi
fi

if [[ -n "$RCLONE_DEST" ]]; then
  if command -v rclone >/dev/null 2>&1; then
    echo "Running rclone copy $DEST_PATH -> $RCLONE_DEST"
    rclone copy "$DEST_PATH" "$RCLONE_DEST"
  else
    echo "rclone not installed; skipping rclone step"
  fi
fi

echo "Done."
