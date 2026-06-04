#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/tags_config.sh"

build_matrix() {

	local gemc_list arch_list
	gemc_list="$(get_gemc_tags)"
	arch_list="$(get_cpu_architectures)"

	local -a gemc_tags arch_tags
	read -r -a gemc_tags <<< "$gemc_list"
	read -r -a arch_tags <<< "$arch_list"

	local body="" sep="" pair os ver
	for gemcv in "${gemc_tags[@]}"; do
		for cpuv in "${arch_tags[@]}"; do
			local runner
			runner="$(get_runner "$cpuv")"
			for pair in "${OS_VERSIONS[@]}"; do
				os="${pair%%=*}"
				ver="${pair#*=}"

				# archlinux is amd64-only
				if [[ "$os" == "archlinux" && "$cpuv" == "arm64" ]]; then
					continue
				fi

				local label gemc_image
				label="${gemcv}-${os}-${ver}-${cpuv}"
				gemc_image="$(build_gemc_image_ref "$gemcv" "$os" "$ver")"

				body+="${sep}{"
				body+="\"label\":\"${label}\","
				body+="\"gemc_image\":\"${gemc_image}\","
				body+="\"runner\":\"${runner}\""
				body+="}"
				sep=","
			done
		done
	done

	local json="{\"include\":[${body}]}"
	if command -v jq >/dev/null 2>&1; then
		printf '%s' "$json" | jq -c .
	else
		printf '%s' "$json"
	fi
}

main() {
	if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
		local DELIM="MATRIX_$(date +%s%N)"
		{
			echo "matrix<<$DELIM"
			build_matrix
			echo "$DELIM"
		} >> "$GITHUB_OUTPUT"
	else
		echo "== matrix =="
		build_matrix
	fi
}

main "$@"
