#!/usr/bin/env bash
# Enforce the chrysa branch model on a pull request.
#
#   develop -> main   release promotion, always allowed
#   hotfix/* -> main  the only other branch allowed to target main
#   type/slug -> *    every other PR, integrated through develop
#
# Inputs: BRANCH_NAME (head ref), BASE_NAME (base ref), BRANCH_PATTERN (optional).
set -euo pipefail

pattern="${BRANCH_PATTERN:-^(feat|feature|fix|chore|docs|refactor|test|ci|build|perf|hotfix)/[a-z0-9._-]+$}"

if [[ "$BASE_NAME" == "main" && "$BRANCH_NAME" == "develop" ]]; then
    echo "Release promotion develop -> main: allowed"
    exit 0
fi

if [[ ! "$BRANCH_NAME" =~ $pattern ]]; then
    echo "::error::Invalid branch name: $BRANCH_NAME"
    echo "Expected: type/short-description (e.g. feat/add-auth-flow)"
    exit 1
fi

if [[ "$BASE_NAME" == "main" && ! "$BRANCH_NAME" =~ ^hotfix/ ]]; then
    echo "::error::PR targets main from '$BRANCH_NAME'."
    echo "Only a release PR from develop, or a hotfix/* branch, may target main."
    exit 1
fi

echo "Branch policy satisfied: $BRANCH_NAME -> $BASE_NAME"
