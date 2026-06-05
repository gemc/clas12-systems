#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/tags_config.sh"

build_matrix_build() {

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

				local label gemc_image platform suffix logs_dir
				label="${os}-${ver}-${cpuv}"
				gemc_image="$(build_gemc_image_ref "$gemcv" "$os" "$ver")"
				platform="linux/$cpuv"
				suffix="-$cpuv"
				logs_dir="logs-${label}"

				body+="${sep}{"
				body+="\"label\":\"${label}\","
				body+="\"gemc_image\":\"${gemc_image}\","
				body+="\"image\":\"${os}\","
				body+="\"image_tag\":\"${ver}\","
				body+="\"gemc_tag\":\"${gemcv}\","
				body+="\"arch\":\"${cpuv}\","
				body+="\"platform\":\"${platform}\","
				body+="\"runner\":\"${runner}\","
				body+="\"suffix\":\"${suffix}\","
				body+="\"logs_dir\":\"${logs_dir}\""
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

build_matrix_manifest() {
	local gemc_list
	gemc_list="$(get_gemc_tags)"

	local -a gemc_tags
	read -r -a gemc_tags <<< "$gemc_list"

	local body="" sep="" pair os ver
	for gemcv in "${gemc_tags[@]}"; do
		for pair in "${OS_VERSIONS[@]}"; do
			os="${pair%%=*}"
			ver="${pair#*=}"

			body+="${sep}{"
			body+="\"label\":\"${os}-${ver}\","
			body+="\"image\":\"${os}\","
			body+="\"image_tag\":\"${ver}\","
			body+="\"gemc_tag\":\"${gemcv}\""
			body+="}"
			sep=","
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
	local image_ref
	image_ref="$(build_image_ref)"

	if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
		local DELIM_BUILD="MATRIX_BUILD_$(date +%s%N)"
		local DELIM_MANIFEST="MATRIX_MANIFEST_$(date +%s%N)"
		{
			echo "matrix_build<<$DELIM_BUILD"
			build_matrix_build
			echo "$DELIM_BUILD"

			echo "matrix_manifest<<$DELIM_MANIFEST"
			build_matrix_manifest
			echo "$DELIM_MANIFEST"

			echo "image=$image_ref"
		} >> "$GITHUB_OUTPUT"
	else
		echo "== matrix_build =="
		build_matrix_build
		echo
		echo "== matrix_manifest =="
		build_matrix_manifest
		echo
		echo "images located at: $image_ref"
	fi
}

main "$@"
