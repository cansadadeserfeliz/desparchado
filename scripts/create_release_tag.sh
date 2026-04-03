#!/usr/bin/env bash
set -euo pipefail  # bash strict mode

if [ $# -ne 1 ]; then
    echo "Usage: $0 <tag-name>" >&2
    exit 1
fi

TAG="$1"
PREVIOUS_BRANCH="$(git symbolic-ref --short HEAD)"

echo "Creating release tag '$TAG'..."

# Always restore the original branch on exit, even if set -e triggers early.
trap 'git checkout "$PREVIOUS_BRANCH" || true' EXIT

git checkout main
git pull origin main

if git tag -l "$TAG" | grep -q "^${TAG}$"; then
    echo "Error: tag '$TAG' already exists locally." >&2
    exit 1
fi

if git ls-remote --tags origin "$TAG" | grep -q "refs/tags/${TAG}$"; then
    echo "Error: tag '$TAG' already exists on remote." >&2
    exit 1
fi

git tag "$TAG"
git push origin "$TAG"

git checkout "$PREVIOUS_BRANCH"

echo "Done. Tag '$TAG' pushed and back on '$PREVIOUS_BRANCH'."
