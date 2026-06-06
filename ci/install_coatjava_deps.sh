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

if command -v java >/dev/null 2>&1 && command -v git-lfs >/dev/null 2>&1 && command -v groovy >/dev/null 2>&1 \
  && command -v jq >/dev/null 2>&1 && command -v mvn >/dev/null 2>&1; then
  set_java_home
  java -version
  git-lfs version
  groovy --version
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

  dnf install -y "$java_pkg" git-lfs groovy jq maven
elif command -v apt-get >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y --no-install-recommends openjdk-21-jdk git-lfs groovy jq maven
elif command -v pacman >/dev/null 2>&1; then
  pacman -Syu --noconfirm --needed jdk21-openjdk git-lfs groovy jq maven
else
  echo "ERROR: unsupported package manager; cannot install Java, Maven, git-lfs, Groovy, and jq" >&2
  exit 2
fi

git lfs install --system || git lfs install
set_java_home
java -version
git-lfs version
groovy --version
mvn -version
