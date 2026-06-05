#!/usr/bin/env bash
set -euo pipefail

if command -v java >/dev/null 2>&1 && command -v git-lfs >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
  java -version
  git-lfs version
  exit 0
fi

if command -v dnf >/dev/null 2>&1; then
  dnf install -y java-21-openjdk-devel git-lfs jq
elif command -v apt-get >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y --no-install-recommends openjdk-21-jdk git-lfs jq
elif command -v pacman >/dev/null 2>&1; then
  pacman -Syu --noconfirm --needed jdk21-openjdk git-lfs jq
else
  echo "ERROR: unsupported package manager; cannot install Java, git-lfs, and jq" >&2
  exit 2
fi

git lfs install --system || git lfs install
java -version
git-lfs version
