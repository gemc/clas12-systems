#!/usr/bin/env bash
set -euo pipefail

# Purpose: profile a CLAS12 configuration under Valgrind's callgrind tool.
#
# gemc itself comes from the base image (ghcr.io/gemc/src); the CLAS12 detector
# digitization plugins and the geometry database are produced by:
#
#   ./ci/build.sh profile
#
# Then, with the Geant4 module loaded and valgrind installed:
#
#   ./ci/profile_gemc.sh -e rga -n 100
#
# The callgrind output file is meant to be opened with qcachegrind / kcachegrind; see the Valgrind
# Profile workflow summary for a reading guide and a per-detector CEst table.

events=100
experiment=rga

usage() {
  cat <<'EOF'

Syntax: profile_gemc.sh [-h] [-e EXPERIMENT] [-n EVENTS]

Options:
  -h            Print this help.
  -e EXPERIMENT Experiment YAML basename under experiments/ (default: rga).
  -n EVENTS     Number of events to profile (default: 100).

EOF
}

while getopts ":he:n:" option; do
  case $option in
    h) usage; exit 0 ;;
    e) experiment="$OPTARG" ;;
    n) events="$OPTARG" ;;
    \?) echo "Error: invalid option -$OPTARG" >&2; usage >&2; exit 1 ;;
  esac
done

repo_root="$PWD"
install_dir="$repo_root/install"
plugindir="$install_dir/lib"
experiments_dir="$repo_root/experiments"
yaml_name="$experiment.yaml"
gemc_bin="$(command -v gemc || true)"

if [[ -z "$gemc_bin" ]]; then
  echo "Error: gemc not found on PATH (load the Geant4 module / base image entrypoint first)." >&2
  exit 1
fi
if [[ ! -f "$experiments_dir/$yaml_name" ]]; then
  echo "Error: experiment card not found: $experiments_dir/$yaml_name" >&2
  exit 1
fi
if [[ ! -f "$experiments_dir/gemc.sqlite" ]]; then
  echo "Error: geometry database not found: $experiments_dir/gemc.sqlite (run ./ci/build.sh profile)." >&2
  exit 1
fi

# CLAS12 detector plugins are discovered through GEMC_PLUGIN_PATH; the clas12-cmag field plugin then
# resolves its field maps from <plugindir>/../fields, so no FIELD_DIR is needed.
export GEMC_PLUGIN_PATH="$plugindir${GEMC_PLUGIN_PATH:+:$GEMC_PLUGIN_PATH}"

output_dir="${PROFILE_OUTPUT_DIR:-$repo_root/profile-logs}"
mkdir -p "$output_dir"
callgrind_out="$output_dir/callgrind.out.$experiment"
gemc_log="$output_dir/gemc.$experiment.log"

# rga.yaml references 'sql: gemc.sqlite' relative to the working directory, so run from experiments/.
cd "$experiments_dir"

echo " > Profiling experiment '$experiment' with $events events under callgrind (single thread)"
echo "   GEMC_PLUGIN_PATH=$GEMC_PLUGIN_PATH"
# Cache and branch simulation add the miss counts the CEst (cycle-estimation) formula needs, so
# qcachegrind and ci/profile_summary.py can report estimated cycles instead of raw instruction reads.
valgrind --tool=callgrind \
  --callgrind-out-file="$callgrind_out" \
  --dump-instr=yes --collect-jumps=yes --skip-plt=yes \
  --cache-sim=yes --branch-sim=yes \
  "$gemc_bin" "$yaml_name" -n="$events" -nthreads=1 | tee "$gemc_log"
exit_code=${PIPESTATUS[0]}

if [[ "$exit_code" -ne 0 ]]; then
  echo " > gemc exited with code $exit_code" >&2
  exit "$exit_code"
fi

echo
echo " > callgrind profile written to $callgrind_out"
echo " > open it with:  qcachegrind $callgrind_out"

# Per-category CEst table (best effort: needs callgrind_annotate from the valgrind package).
summary_md="$output_dir/summary.$experiment.md"
if command -v callgrind_annotate >/dev/null 2>&1; then
  echo " > Writing category summary to $summary_md"
  python3 "$repo_root/ci/profile_summary.py" "$callgrind_out" --title "$experiment" > "$summary_md" || \
    echo " > Category summary generation failed; the callgrind file is still available."
else
  echo " > callgrind_annotate not found; skipping the category summary."
fi

# Show the table in this job's own summary too, so it does not depend on the artifact round-trip.
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
  if [[ -s "$summary_md" ]]; then
    cat "$summary_md" >> "$GITHUB_STEP_SUMMARY"
  else
    echo "_No category table was produced for $experiment (see the job log)._" >> "$GITHUB_STEP_SUMMARY"
  fi
fi

echo " > Category summary:"
cat "$summary_md" 2>/dev/null || echo "   (none)"
ls -l "$output_dir"
echo
