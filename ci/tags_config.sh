#!/usr/bin/env bash

# Shared CI configuration: which base images to build CLAS12 systems against.
# Keep versions here so they stay in sync across all ci/ scripts.
#
# All container builds use g4install (Geant4 only) and compile GEMC from the gemc subproject.
# GEMC tags name the published CLAS12 images; Geant4 tags select their base images.
get_gemc_tags()         { echo "dev"; }         # space-separated published CLAS12 image tags
get_geant4_tags()       { echo "11.4.3"; }      # space-separated g4install image tags
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

# Returns the multi-arch manifest tag for a Geant4-only base image.
build_g4install_image_ref() {
	local g4_tag="$1" os="$2" os_ver="$3"
	printf 'ghcr.io/gemc/g4install:%s-%s-%s' "$g4_tag" "$os" "$os_ver"
}

build_image_ref() {
	local owner="${GITHUB_REPOSITORY_OWNER:-gemc}"
	local repo_full="${GITHUB_REPOSITORY:-gemc/clas12-systems}"
	local repo="${repo_full##*/}"
	printf 'ghcr.io/%s/%s' "$(lc "$owner")" "$(lc "$repo")"
}
