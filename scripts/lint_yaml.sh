#!/usr/bin/env bash
# yamllint over every YAML file, minus the excluded path patterns.
set -euo pipefail

config_file="${CONFIG_FILE:-.yamllint.yaml}"
read -r -a excludes <<<"${EXCLUDE_PATHS:-}"

find_args=(. \( -name "*.yml" -o -name "*.yaml" \))
for pattern in "${excludes[@]}"; do
    find_args+=(-not -path "$pattern")
done

mapfile -t files < <(find "${find_args[@]}")
if [ ${#files[@]} -eq 0 ]; then
    echo "No YAML files found, skipping."
    exit 0
fi

yamllint --config-file "$config_file" "${files[@]}"
