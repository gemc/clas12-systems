#!/usr/bin/env bash
set -euo pipefail

# Build CLAS12 systems inside published GEMC base images from ghcr.io/gemc/src.
# Optional argument: address, thread, undefined, or leak to enable a sanitizer.

git config --global --add safe.directory '*'

export DOCKER_ENTRYPOINT_SOURCE_ONLY=1
. /usr/local/bin/docker-entrypoint.sh

export PKG_CONFIG_PATH="${SIM_HOME}/gemc/dev/lib/pkgconfig${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}"

jobs=$(nproc 2>/dev/null || echo 4)
jobs=$(( jobs < 16 ? jobs : 16 ))

sanitizer="${1:-}"
setup_options=(
  "--wipe"
  "--prefix=$PWD/install"
)

case "$sanitizer" in
  "")
    setup_options+=("-Dbuildtype=release")
    ;;
  address|thread|undefined|leak)
    setup_options+=("-Dbuildtype=debug" "-Dclas12_sanitize=$sanitizer")
    ;;
  *)
    echo "Unsupported sanitizer: $sanitizer" >&2
    exit 2
    ;;
esac

mkdir -p logs
setup_log="$PWD/logs/setup.log"
compile_log="$PWD/logs/compile.log"
install_log="$PWD/logs/install.log"
test_log="$PWD/logs/test.log"

{
  echo " > geant4-config  : $(command -v geant4-config) $(geant4-config --version)"
  echo " > gemc           : $(command -v gemc || true)"
  echo " > meson          : $(command -v meson) $(meson --version)"
  echo " > SIM_HOME       : ${SIM_HOME}"
  echo " > PKG_CONFIG_PATH: ${PKG_CONFIG_PATH}"
  echo " > sanitizer      : ${sanitizer:-none}"
  echo " > cores          : ${jobs}"
  echo
} | tee "$setup_log"

echo " > meson setup build ${setup_options[*]}" | tee -a "$setup_log"
if ! meson setup build "${setup_options[@]}" >> "$setup_log" 2>&1; then
  echo " > Meson configure failed. Log:"
  cat "$setup_log"
  exit 1
fi

echo " > meson compile -C build -j $jobs" | tee "$compile_log"
if ! meson compile -C build -j "$jobs" >> "$compile_log" 2>&1; then
  echo " > Meson compile failed. Log:"
  cat "$compile_log"
  exit 1
fi

echo " > meson install -C build" | tee "$install_log"
if ! meson install -C build >> "$install_log" 2>&1; then
  echo " > Meson install failed. Log:"
  cat "$install_log"
  exit 1
fi

echo " > meson test -C build" | tee "$test_log"
if ! meson test -C build --print-errorlogs -j 1 --no-rebuild --num-processes 1 -v >> "$test_log" 2>&1; then
  echo " > Meson tests failed. Log:"
  cat "$test_log"
  exit 1
fi

echo " > build, install, and tests complete"
