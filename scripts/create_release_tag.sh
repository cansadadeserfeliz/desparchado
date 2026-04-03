#!/usr/bin/env bash
set -euo pipefail  # bash strict mode

if [ $# -ne 1 ]; then
    echo "Usage: $0 <tag-name>" >&2
    exit 1
fi

TAG="$1"
PREVIOUS_BRANCH="$(git symbolic-ref --short HEAD)"

echo "Creating release tag '$TAG'..."

git checkout main
git pull origin main
git tag "$TAG"
git push origin "$TAG"

git checkout "$PREVIOUS_BRANCH"

echo "Done. Tag '$TAG' pushed and back on '$PREVIOUS_BRANCH'."
