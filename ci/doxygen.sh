#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

command -v doxygen >/dev/null 2>&1 || {
  echo "ERROR: doxygen not found in PATH" >&2
  exit 2
}

rm -rf pages
mkdir -p pages

ci/create_doxygen.sh "clas12-systems"
doxygen Doxyfile

cp -f ci/mydoxygen.css pages/html/mydoxygen.css 2>/dev/null || true
test -f pages/html/index.html

cp -f pages/html/index.html pages/index.html
echo "Done. Output in ./pages/"
