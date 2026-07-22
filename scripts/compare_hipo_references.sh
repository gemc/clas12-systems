#!/usr/bin/env bash
#
# Download the published HIPO references for one detector and run the hipo-histos comparison
# locally, reproducing the CI job in .github/workflows/hipo_histos_compare.yml.
#
# Two rolling releases are involved (always latest, never pinned):
#   - clas12Tags (GEMC2) reference: gemc/clas12Tags @ histo-reference
#       <system>_reference.hipo            (with field)
#       <system>_reference_nofield.hipo    (-no_field=all)
#   - clas12-systems (GEMC3) output: gemc/clas12-systems @ histo-gemc3
#       <system>_gemc3.hipo                (with field)
#       <system>_gemc3_nofield.hipo        (-no_field=all)
#
# For each requested variant (field / nofield) the script downloads the matching pair and runs
# `hipo-histos --compare-system <system> <reference> <gemc3>`, the same invocation CI uses.
#
# Usage:
#   scripts/compare_hipo_references.sh <detector> [options]
#
#   <detector>                  one of: dc ec ftof ltcc pcal
#
# Options:
#   --variant <field|nofield|both>   which reference variant(s) to compare (default: both)
#   --hipo-histos <path>             hipo-histos executable (default: auto-detect, see below)
#   --out-dir <dir>                  output directory (default: ./hipo_compare/<detector>)
#   --plot-format <fmt>             ROOT plot format: png pdf ... (default: png)
#   --no-download                   reuse already-downloaded HIPOs in --out-dir
#   --fail-on-diff                   exit non-zero if a comparison reports a difference
#   -h, --help                       show this help and exit
#
# Examples:
#   scripts/compare_hipo_references.sh dc
#   scripts/compare_hipo_references.sh ec --variant nofield --fail-on-diff
#   scripts/compare_hipo_references.sh ftof --hipo-histos build/hipo-histos/hipo-histos
#   scripts/compare_hipo_references.sh ltcc --variant field

set -euo pipefail

REFERENCE_REPO="gemc/clas12Tags"
REFERENCE_TAG="histo-reference"
GEMC3_REPO="gemc/clas12-systems"
GEMC3_TAG="histo-gemc3"
SUPPORTED_SYSTEMS=(dc ec ftof ltcc pcal)

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --------------------------------------------------------------------------------------------
# Argument parsing
# --------------------------------------------------------------------------------------------
usage() { sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'; }

system=""
variant="both"
hipo_histos=""
out_dir=""
plot_format="png"
do_download=1
fail_on_diff=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --variant)      variant="$2"; shift 2 ;;
    --hipo-histos)  hipo_histos="$2"; shift 2 ;;
    --out-dir)      out_dir="$2"; shift 2 ;;
    --plot-format)  plot_format="$2"; shift 2 ;;
    --no-download)  do_download=0; shift ;;
    --fail-on-diff) fail_on_diff=1; shift ;;
    -*) echo "ERROR: unknown option '$1'" >&2; usage >&2; exit 2 ;;
    *)
      if [[ -z "$system" ]]; then system="$1"; shift
      else echo "ERROR: unexpected argument '$1'" >&2; exit 2; fi ;;
  esac
done

if [[ -z "$system" ]]; then
  echo "ERROR: missing <detector> argument" >&2
  usage >&2
  exit 2
fi
if [[ ! " ${SUPPORTED_SYSTEMS[*]} " == *" $system "* ]]; then
  echo "ERROR: unsupported detector '$system' (supported: ${SUPPORTED_SYSTEMS[*]})" >&2
  exit 2
fi

case "$variant" in
  field)   variants=(field) ;;
  nofield) variants=(nofield) ;;
  both)    variants=(field nofield) ;;
  *) echo "ERROR: --variant must be field, nofield or both (got '$variant')" >&2; exit 2 ;;
esac

[[ -n "$out_dir" ]] || out_dir="$REPO_ROOT/hipo_compare/$system"
mkdir -p "$out_dir"

# --------------------------------------------------------------------------------------------
# Locate hipo-histos
# --------------------------------------------------------------------------------------------
if [[ -z "$hipo_histos" ]]; then
  for candidate in \
    "${HIPO_HISTOS:-}" \
    "$REPO_ROOT/install/bin/hipo-histos" \
    "$REPO_ROOT/build/hipo-histos/hipo-histos" \
    "$(command -v hipo-histos 2>/dev/null || true)"; do
    if [[ -n "$candidate" && -x "$candidate" ]]; then hipo_histos="$candidate"; break; fi
  done
fi
if [[ -z "$hipo_histos" || ! -x "$hipo_histos" ]]; then
  echo "ERROR: hipo-histos executable not found. Build the repo (ci/build.sh) or pass" >&2
  echo "       --hipo-histos <path> (or set HIPO_HISTOS=<path>)." >&2
  exit 1
fi
echo "Using hipo-histos: $hipo_histos"

# --------------------------------------------------------------------------------------------
# Download helper
# --------------------------------------------------------------------------------------------
download() {
  # download <repo> <tag> <asset> <dest>
  local repo="$1" tag="$2" asset="$3" dest="$4"
  local url="https://github.com/${repo}/releases/download/${tag}/${asset}"
  if [[ "$do_download" -eq 0 && -s "$dest" ]]; then
    echo "  reuse  $dest"
    return 0
  fi
  echo "  fetch  $url"
  curl -fSL "$url" -o "$dest"
}

# --------------------------------------------------------------------------------------------
# Per-variant download + compare
# --------------------------------------------------------------------------------------------
overall_status=0

for v in "${variants[@]}"; do
  suffix=""; [[ "$v" == nofield ]] && suffix="_nofield"

  ref_hipo="$out_dir/${system}_reference${suffix}.hipo"
  gemc3_hipo="$out_dir/${system}_gemc3${suffix}.hipo"

  echo
  echo "=== $system / $v ==="
  download "$REFERENCE_REPO" "$REFERENCE_TAG" "${system}_reference${suffix}.hipo"     "$ref_hipo"
  download "$REFERENCE_REPO" "$REFERENCE_TAG" "${system}_reference${suffix}.txt" \
    "$out_dir/${system}_reference${suffix}.txt" || true
  download "$GEMC3_REPO"     "$GEMC3_TAG"     "${system}_gemc3${suffix}.hipo"         "$gemc3_hipo"
  download "$GEMC3_REPO"     "$GEMC3_TAG"     "${system}_gemc3.txt" \
    "$out_dir/${system}_gemc3.txt" || true

  compare_dir="$out_dir/compare_${v}"
  mkdir -p "$compare_dir/plots"

  extra=()
  [[ "$fail_on_diff" -eq 1 ]] && extra+=(--fail-on-diff --max-integral-diff 0.1)

  set +e
  "$hipo_histos" \
    --compare-system "$system" \
    "$ref_hipo" "$gemc3_hipo" \
    --label "clas12Tags-${v}" --label gemc3 \
    --diagnostics \
    --plot-format "$plot_format" \
    -o "$compare_dir/${system}_compare.root" \
    --plot-dir "$compare_dir/plots" \
    ${extra[@]+"${extra[@]}"} \
    2>&1 | tee "$compare_dir/compare.log"
  status=${PIPESTATUS[0]}
  set -e

  echo "  result ($v): $([[ "$status" -eq 0 ]] && echo PASS || echo FAIL) (exit $status)"
  echo "  plots:  $compare_dir/plots"
  [[ "$status" -ne 0 ]] && overall_status=1
done

echo
echo "Outputs under: $out_dir"
exit "$overall_status"
