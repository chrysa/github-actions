#!/usr/bin/env bash
# Compute the next SETUP_VERSION for the multi-machine setup gist and write it to the
# version-carrying scripts. Emits `current` and `next` to $GITHUB_OUTPUT.
#
# Inputs: GIST_DIR, BUMP_OVERRIDE (patch|minor|major, optional), COMMIT_SUBJECT.
set -euo pipefail

gist_dir="${GIST_DIR:-docs/multi-machine-setup/gist}"

kind="patch"
if [[ "${COMMIT_SUBJECT:-}" =~ BREAKING\ CHANGE|! ]]; then
    kind="major"
elif [[ "${COMMIT_SUBJECT:-}" =~ ^feat\( ]]; then
    kind="minor"
fi
[[ -n "${BUMP_OVERRIDE:-}" ]] && kind="$BUMP_OVERRIDE"

current="$(grep -m1 '^SETUP_VERSION=' "$gist_dir/setup-linux.sh" | sed -E 's/.*"([^"]+)".*/\1/')"
IFS='.' read -r major minor patch <<<"$current"
case "$kind" in
    major) major=$((major + 1)); minor=0; patch=0 ;;
    minor) minor=$((minor + 1)); patch=0 ;;
    patch) patch=$((patch + 1)) ;;
    *) echo "::error::unknown bump kind: $kind"; exit 1 ;;
esac
next="${major}.${minor}.${patch}"

sed -i -E "s/^SETUP_VERSION=\"[^\"]+\"/SETUP_VERSION=\"${next}\"/" "$gist_dir/setup-linux.sh"
sed -i -E "s/^\\\$SetupVersion = '[^']+'/\$SetupVersion = '${next}'/" "$gist_dir/setup-windows.ps1"

{
    echo "current=$current"
    echo "next=$next"
} >>"$GITHUB_OUTPUT"
echo "Bumping $current → $next ($kind)"
