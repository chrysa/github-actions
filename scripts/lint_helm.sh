#!/usr/bin/env bash
# helm dependency update + helm lint --strict on every chart under the charts root.
set -uo pipefail

charts_root="${CHARTS_ROOT:-apps}"

while read -r name url; do
    [[ -z "${name:-}" ]] && continue
    helm repo add "$name" "$url"
done <<<"${HELM_REPOSITORIES:-}"
[[ -n "${HELM_REPOSITORIES:-}" ]] && helm repo update

mapfile -t charts < <(find "$charts_root" -mindepth 2 -maxdepth 2 -name "Chart.yaml" -printf '%h\n')
if [[ ${#charts[@]} -eq 0 ]]; then
    echo "No chart found under ${charts_root}, skipping."
    exit 0
fi

errors=0
for chart in "${charts[@]}"; do
    echo "→ dependency update: $chart"
    helm dependency update "$chart" >/dev/null 2>&1 || true
    echo "→ lint: $chart"
    helm lint "$chart" --strict || errors=$((errors + 1))
done
exit "$errors"
