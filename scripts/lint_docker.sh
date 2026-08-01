#!/usr/bin/env bash
# Install hadolint and lint every Dockerfile, minus the excluded path patterns.
set -euo pipefail

version="${HADOLINT_VERSION:-v2.14.0}"
curl --proto "=https" --tlsv1.2 -fsSL "https://github.com/hadolint/hadolint/releases/download/${version}/hadolint-Linux-x86_64" \
    -o /usr/local/bin/hadolint
chmod +x /usr/local/bin/hadolint

read -r -a excludes <<<"${EXCLUDE_PATHS:-}"
find_args=(. \( -name "Dockerfile" -o -name "*.Dockerfile" \))
for pattern in "${excludes[@]}"; do
    find_args+=(-not -path "$pattern")
done

mapfile -t dockerfiles < <(find "${find_args[@]}")
if [[ ${#dockerfiles[@]} -eq 0 ]]; then
    echo "No Dockerfiles found, skipping."
    exit 0
fi

hadolint --failure-threshold "${FAILURE_THRESHOLD:-warning}" "${dockerfiles[@]}"
