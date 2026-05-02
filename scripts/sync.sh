#!/usr/bin/env bash
# scripts/sync.sh — pull others' changes, then push yours.
#
# Run this every 20-30 min, or whenever you finish a task.
# Uses --rebase --autostash so any work-in-progress is stashed,
# remote commits land first, then your work is reapplied on top.

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    echo "✗ you're on '$CURRENT_BRANCH', not 'main'."
    echo "  this script only syncs main. switch with: git checkout main"
    exit 1
fi

echo "→ syncing with origin/main"
if ! git pull --rebase --autostash origin main; then
    echo
    echo "✗ rebase paused on a conflict."
    echo "  resolve files, then run:"
    echo "    git add <resolved-files>"
    echo "    git rebase --continue"
    echo "    bash scripts/sync.sh"
    exit 1
fi

if [[ -n "$(git log @{u}..HEAD --oneline 2>/dev/null)" ]]; then
    echo "→ pushing your commits"
    git push origin main
fi

echo "✓ in sync"
