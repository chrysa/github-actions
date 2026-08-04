#!/usr/bin/env bash
# Prepend a Keep a Changelog entry for the new version, built from the commits touching
# the watched directory since the previous setup-v* tag.
# Inputs: GIST_DIR, WATCH_DIR, NEW_VERSION, ENTRY_DATE.
set -euo pipefail

gist_dir="${GIST_DIR:-docs/multi-machine-setup/gist}"
watch_dir="${WATCH_DIR:-docs/multi-machine-setup}"
changelog="$gist_dir/CHANGELOG.md"
previous_tag="$(git tag --list 'setup-v*' --sort=-v:refname | head -1)"
range="${previous_tag:+${previous_tag}..}HEAD"

entry="$(mktemp)"
{
    echo "## [${NEW_VERSION}] - ${ENTRY_DATE}"
    echo ""
    git log --pretty='- %s (%h)' "$range" -- "$watch_dir" | head -30
    echo ""
} >"$entry"

if [[ ! -f "$changelog" ]]; then
    {
        echo "# Changelog · multi-machine setup"
        echo ""
        echo "All notable changes follow [Keep a Changelog](https://keepachangelog.com)."
        echo ""
    } >"$changelog"
fi

merged="$(mktemp)"
head -4 "$changelog" >"$merged"
cat "$entry" >>"$merged"
tail -n +5 "$changelog" >>"$merged"
mv "$merged" "$changelog"
