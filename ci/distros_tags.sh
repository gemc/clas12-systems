#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/tags_config.sh"

build_matrix_build() {

	# All container workflows build CLAS12 systems FROM SCRATCH on g4install (Geant4-only) images: no GEMC
	# is pre-installed, so the build compiles it from the gemc subproject. The matrix therefore
	# iterates Geant4 image tags, and each entry carries geant4_tag so the workflow can
	# `module load geant4/<tag>` before building.
	local g4_list arch_list gemc_tag
	gemc_tag="$(get_gemc_tags | awk '{print $1}')"
	g4_list="$(get_geant4_tags)"
	arch_list="$(get_cpu_architectures)"

	local -a g4_tags arch_tags
	read -r -a g4_tags <<< "$g4_list"
	read -r -a arch_tags <<< "$arch_list"

	local body="" sep="" pair os ver
	for g4v in "${g4_tags[@]}"; do
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

				local label container_image platform suffix logs_dir
				label="${os}-${ver}-${cpuv}"
				container_image="$(build_g4install_image_ref "$g4v" "$os" "$ver")"
				platform="linux/$cpuv"
				suffix="-$cpuv"
				logs_dir="logs-${label}"

				body+="${sep}{"
				body+="\"label\":\"${label}\","
				body+="\"container_image\":\"${container_image}\","
				body+="\"image\":\"${os}\","
				body+="\"image_tag\":\"${ver}\","
				body+="\"geant4_tag\":\"${g4v}\","
				body+="\"gemc_tag\":\"${gemc_tag}\","
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
