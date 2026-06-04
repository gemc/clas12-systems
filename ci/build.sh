#!/usr/bin/env bash
set -euo pipefail

# Recent Git refuses to operate on a repository owned by a different UID.
git config --global --add safe.directory '*'

# Source the GEMC container entrypoint.  This initialises the Environment
# Modules system, loads the Geant4 module (which sets SIM_HOME and adds
# Geant4 to PKG_CONFIG_PATH), and exports the GEMC binary path.
DOCKER_ENTRYPOINT_SOURCE_ONLY=1 . /usr/local/bin/docker-entrypoint.sh

# Make the installed GEMC pkgconfig visible so meson can find the gemc dep.
export PKG_CONFIG_PATH="${SIM_HOME}/gemc/dev/lib/pkgconfig${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}"

jobs=$(nproc 2>/dev/null || echo 4)
jobs=$(( jobs < 16 ? jobs : 16 ))

{
  echo " > geant4-config : $(command -v geant4-config) $(geant4-config --version)"
  echo " > meson         : $(command -v meson) $(meson --version)"
  echo " > SIM_HOME      : ${SIM_HOME}"
  echo " > PKG_CONFIG_PATH: ${PKG_CONFIG_PATH}"
  echo " > cores         : ${jobs}"
  echo
}

echo " > meson setup"
meson setup build --wipe -Dbuildtype=release

echo " > meson compile"
meson compile -C build -j "$jobs"

echo " > build complete"
