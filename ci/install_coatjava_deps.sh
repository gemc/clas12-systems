#!/usr/bin/env bash
set -euo pipefail

set_java_home() {
  if [[ -n "${JAVA_HOME:-}" && -x "${JAVA_HOME}/bin/java" ]]; then
    export JAVA_HOME
    return 0
  fi

  local java_bin java_real
  java_bin="$(command -v java || true)"
  if [[ -z "$java_bin" ]]; then
    echo "ERROR: java not found; cannot set JAVA_HOME" >&2
    return 1
  fi

  java_real="$(readlink -f "$java_bin" 2>/dev/null || true)"
  if [[ -z "$java_real" ]]; then
    java_real="$java_bin"
  fi

  JAVA_HOME="$(cd "$(dirname "$java_real")/.." && pwd)"
  export JAVA_HOME
}

# GEMC compiles GUI catalogs with Qt 6 Linguist tools, also in CLAS12 source builds.
qt_lrelease_available() {
  local tool
  for tool in lrelease6 lrelease-qt6 /usr/lib/qt6/bin/lrelease /usr/lib64/qt6/bin/lrelease; do
    if command -v "$tool" >/dev/null 2>&1; then return 0; fi
  done
  return 1
}

if command -v java >/dev/null 2>&1 && command -v git-lfs >/dev/null 2>&1 && command -v jq >/dev/null 2>&1 \
  && command -v mvn >/dev/null 2>&1 && qt_lrelease_available; then
  set_java_home
  java -version
  git-lfs version
  mvn -version
  exit 0
fi

if command -v dnf >/dev/null 2>&1; then
  java_pkg=""
  for candidate in java-21-openjdk-devel java-latest-openjdk-devel java-17-openjdk-devel; do
    if dnf list --available "$candidate" >/dev/null 2>&1 \
      || dnf list --installed "$candidate" >/dev/null 2>&1; then
      java_pkg="$candidate"
      break
    fi
  done

  if [[ -z "$java_pkg" ]]; then
    echo "ERROR: no supported OpenJDK devel package found" >&2
    exit 1
  fi

  dnf install -y "$java_pkg" git-lfs jq maven qt6-qttools-devel qt6-qttranslations
elif command -v apt-get >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y --no-install-recommends openjdk-21-jdk git-lfs jq maven qt6-l10n-tools qt6-translations-l10n
elif command -v pacman >/dev/null 2>&1; then
  pacman -Syu --noconfirm --needed jdk21-openjdk git-lfs jq maven qt6-tools qt6-translations
else
  echo "ERROR: unsupported package manager; cannot install Java, Maven, git-lfs, and jq" >&2
  exit 2
fi

git lfs install --system || git lfs install
set_java_home
java -version
git-lfs version
mvn -version
