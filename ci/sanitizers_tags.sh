#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/tags_config.sh"

# full sanitizers:
# on macOS, LeakSanitizer (LSan) support is materially less uniform and
# more fragile across toolchains and architectures than ASan/UBSan/TSan.
# macos:  address, thread, undefined
# linux:  address, thread, undefined, leak
#
# In the CI we first run one sanitizer at a time until all issues are solved
# Then we can run them all
get_sanitizers() {
  local choice_of_sanitizer="undefined"
  local baseos=$1
	case "$baseos" in
	  "macos") echo $choice_of_sanitizer ;;
	  "ubuntu" | "fedora" | "almalinux" | "debian" | "archlinux")	echo $choice_of_sanitizer ;;
		*)
			echo   "ERROR: unsupported baseos $baseos" >&2
			return 2
			;;
	esac

}

build_matrix_build() {

	local arch_list gemc_list
	arch_list="$(get_cpu_architectures)"
	gemc_list="$(get_gemc_tags)"

	local -a arch_tags gemc_tags
	read -r -a arch_tags <<<"$arch_list"
	read -r -a gemc_tags <<<"$gemc_list"

	local body="" sep="" pair os ver
	for cpuv in "${arch_tags[@]}"; do
		for gemcv in "${gemc_tags[@]}"; do
			for pair in "${OS_VERSIONS[@]}"; do
				os="${pair%%=*}"
				ver="${pair#*=}"

				local runner
				runner="$(get_runner "$cpuv")"

				local sanitizer_list sanitizer_tags
				sanitizer_list="$(get_sanitizers "$os")"
				read -r -a sanitizer_tags <<<"$sanitizer_list"
				for sanitizer in "${sanitizer_tags[@]}"; do

					# archlinux is amd64-only
					if [[ "$os" == "archlinux" && "$cpuv" == "arm64" ]]; then
						continue
					fi

					local label gemc_image
					label="${os}-${ver}-${cpuv}"
					gemc_image="$(build_gemc_image_ref "$gemcv" "$os" "$ver")"

					body+="${sep}{"
					body+="\"label\":\"${label}\","
					body+="\"gemc_image\":\"${gemc_image}\","
					body+="\"baseos\":\"${os}\","
					body+="\"baseos_tag\":\"${ver}\","
					body+="\"runner\":\"${runner}\","
					body+="\"gemc_tag\":\"${gemcv}\","
					body+="\"arch\":\"${cpuv}\","
					body+="\"sanitizer\":\"${sanitizer}\""
					body+="}"
					sep=","
				done
			done
		done
	done

	local json="{\"include\":[${body}]}"
	if command -v jq >/dev/null 2>&1; then
	#	printf '%s' "$json"
		printf '%s' "$json" | jq -c .
	else
		printf '%s' "$json"
	fi
}
# the separate matrices are needed so that manifest is not run twice
main() {
	if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
		local DELIM_BUILD="MATRIX_SANITIZE_$(date +%s%N)"
		{
			echo "matrix_sanitize<<$DELIM_BUILD"
			build_matrix_build
			echo "$DELIM_BUILD"
		} >>"$GITHUB_OUTPUT"
	else
		echo "== matrix_sanitize =="
		build_matrix_build
		echo
	fi

}

main "$@"
