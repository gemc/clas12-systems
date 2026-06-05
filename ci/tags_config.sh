#!/usr/bin/env bash

# Shared CI configuration: which GEMC base images to build CLAS12 systems against.
# Keep versions here so they stay in sync across all ci/ scripts.

get_gemc_tags()         { echo "dev"; }         # space-separated list
get_cpu_architectures() { echo "arm64 amd64"; } # space-separated list

get_runner() {
	local arch=$1
	case "$arch" in
		"arm64") echo "ubuntu-24.04-arm" ;;
		"amd64") echo "ubuntu-latest" ;;
		*)
			echo "ERROR: unsupported arch $arch" >&2
			return 2
			;;
	esac
}

lc() { printf '%s' "$1" | tr '[:upper:]' '[:lower:]'; }

OS_VERSIONS=(
  "ubuntu=24.04"
  "ubuntu=26.04"
  "fedora=44"
  "almalinux=10"
  "debian=13"
  "archlinux=latest"
)

# Returns the multi-arch manifest tag for a GEMC image.
# The manifest resolves to the correct arch based on the runner.
build_gemc_image_ref() {
	local gemc_tag="$1" os="$2" os_ver="$3"
	printf 'ghcr.io/gemc/src:%s-%s-%s' "$gemc_tag" "$os" "$os_ver"
}

build_image_ref() {
	local owner="${GITHUB_REPOSITORY_OWNER:-gemc}"
	local repo_full="${GITHUB_REPOSITORY:-gemc/clas12-systems}"
	local repo="${repo_full##*/}"
	printf 'ghcr.io/%s/%s' "$(lc "$owner")" "$(lc "$repo")"
}
