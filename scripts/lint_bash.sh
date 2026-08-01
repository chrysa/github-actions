#!/usr/bin/env bash
# Run shellcheck and shfmt over every shell script, minus the excluded path patterns.
set -euo pipefail

read -r -a excludes <<<"${EXCLUDE_PATHS:-}"
find_args=(. -name "*.sh")
for pattern in "${excludes[@]}"; do
    find_args+=(-not -path "$pattern")
done

mapfile -t scripts < <(find "${find_args[@]}")
if [ ${#scripts[@]} -eq 0 ]; then
    echo "No shell scripts found, skipping."
    exit 0
fi

shellcheck --severity="${SHELLCHECK_SEVERITY:-error}" "${scripts[@]}"
shfmt -d -i "${SHFMT_INDENT:-4}" "${scripts[@]}" || true
