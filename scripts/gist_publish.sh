#!/usr/bin/env bash
# Commit the version bump, tag it, and push the gist files.
# Inputs: WATCH_DIR, GIST_DIR, NEW_VERSION, GIST_ID (optional), GH_TOKEN.
set -euo pipefail

watch_dir="${WATCH_DIR:-docs/multi-machine-setup}"
gist_dir="${GIST_DIR:-docs/multi-machine-setup/gist}"

git config user.name 'chrysa-bot'
git config user.email 'bot@chrysa.dev'
git add "$watch_dir"
if ! git commit -m "chore(setup): bump v${NEW_VERSION}"; then
    echo "Nothing to commit — skipping publish."
    exit 0
fi
git tag "setup-v${NEW_VERSION}"
git push origin HEAD --tags

if [[ -z "${GIST_ID:-}" ]]; then
    echo "::warning::gist id absent · skip gist publish"
    exit 0
fi

cd "$gist_dir"
gh gist edit "$GIST_ID" \
    --add setup-linux.sh \
    --add setup-windows.ps1 \
    --add README.md \
    --add CHANGELOG.md
echo "Gist updated · v${NEW_VERSION}"
