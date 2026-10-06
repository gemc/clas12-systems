#!/usr/bin/env bash
# Source this file before configuring or running GEMC in a g4install container.

clas12_ci_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$clas12_ci_dir/tags_config.sh"
export DOCKER_ENTRYPOINT_SOURCE_ONLY=1
. /usr/local/bin/docker-entrypoint.sh
module load "geant4/${GEANT4_TAG:-$(get_geant4_tags | awk '{print $1}')}"

clas12_ci_prefix="$(dirname "$clas12_ci_dir")/install"
export PATH="${clas12_ci_prefix}/bin:${PATH}"
export LD_LIBRARY_PATH="${clas12_ci_prefix}/lib:${LD_LIBRARY_PATH:-}"
export PKG_CONFIG_PATH="${clas12_ci_prefix}/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
