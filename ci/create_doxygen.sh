#!/usr/bin/env bash
set -euo pipefail

project_name="${1:-clas12-systems}"

doxygen -g Doxyfile >/dev/null 2>&1

set_key() {
  local key="$1"
  local value="$2"
  if grep -qE "^${key}[[:space:]]*=" Doxyfile; then
    sed -i "s|^${key}[[:space:]]*=.*|${key} = ${value}|g" Doxyfile
  else
    printf '%s = %s\n' "$key" "$value" >> Doxyfile
  fi
}

set_key PROJECT_NAME "\"${project_name}\""
set_key OUTPUT_DIRECTORY pages
set_key INPUT "README.md meson.build geometry_src ci"
set_key RECURSIVE YES
set_key EXTRACT_ALL YES
set_key SOURCE_BROWSER YES
set_key GENERATE_LATEX NO
set_key GENERATE_TREEVIEW YES
set_key HTML_EXTRA_STYLESHEET ci/mydoxygen.css
set_key FILE_PATTERNS "*.h *.hh *.hpp *.hxx *.c *.cc *.cpp *.cxx *.py *.sh *.md meson.build"
set_key EXCLUDE_PATTERNS "*/.git/* */build/* */subprojects/* */geometry_src/coatjava/* */geometry_src/coatjava_src/*"
