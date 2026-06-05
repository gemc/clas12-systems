#!/usr/bin/env bash
set -euo pipefail

./ci/install_coatjava_deps.sh

if [[ -d geometry_src/coatjava ]]; then
  echo " > coatjava already installed in geometry_src/coatjava"
  exit 0
fi

echo " > installing coatjava"
git lfs install
./geometry_src/install_coatjava.sh -l
