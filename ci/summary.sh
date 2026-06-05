#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ci/summary.sh [SUMMARY_FILE]
# If SUMMARY_FILE is omitted, uses $GITHUB_STEP_SUMMARY.

summary_file="${1:-${GITHUB_STEP_SUMMARY:-}}"
if [[ -z "${summary_file}" ]]; then
  printf 'ERROR: summary file not provided and GITHUB_STEP_SUMMARY is empty\n' >&2
  exit 2
fi

{
  printf '# CLAS12 Systems — Overview\n'
  printf 'This workflow builds CLAS12 systems images from published GEMC bases at [ghcr.io/gemc/src](https://github.com/gemc/src/pkgs/container/src).\n'
  printf 'Except for archlinux (amd64-only), the matrix runs on both the *amd64* and *arm64* architectures.\n'
  printf '\n'
  printf '\n'
  printf 'Set these convenience variables for interactive image use below (choose your own password)\n'
  printf '```bash\n'
  printf 'VPORTS=(-p 6080:6080 -p 5900:5900)\n'
  printf 'VNC_PASS=(-e X11VNC_PASSWORD=change-me)\n'
  printf 'VNC_BIND=(-e VNC_BIND=0.0.0.0)\n'
  printf 'GEO_FLAGS=(-e GEOMETRY=1920x1200)\n'
  printf '```\n'
  printf '\n'
  printf 'If your CPU is arm64 and you want to use the archlinux image, add this to Docker command lines:\n'
  printf '```bash\n'
  printf -- '--platform=linux/amd64\n'
  printf '```\n'
  printf -- '---\n'
} >> "${summary_file}"
