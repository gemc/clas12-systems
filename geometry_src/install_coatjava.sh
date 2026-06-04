#!/bin/zsh

set -euo pipefail

function printHelp() {
	cat <<EOF
Usage: install_coatjava.sh [-l | -t tag | -g github_url]

Options:
  -l                 use latest coatjava tag (default)
  -t <tag>           use a specific coatjava tag, like 14.1.0
  -g <github_url>    clone and build a custom coatjava repository
  -h                 show this help
EOF
}

# development. Set to no to use coatjava distribution instead
USEDEVEL="no"
githubRepo="https://github.com/JeffersonLab/coatjava"
COATJAVA_TAG=""
coatjava_choice_count=0
log_file="../build_coatjava.log"

REPO="JeffersonLab/coatjava"

while getopts ":lt:g:h" opt; do
	case "$opt" in
	l)
		USEDEVEL="no"
		coatjava_choice_count=$((coatjava_choice_count + 1))
		;;
	t)
		COATJAVA_TAG="$OPTARG"
		USEDEVEL="no"
		coatjava_choice_count=$((coatjava_choice_count + 1))
		;;
	g)
		githubRepo="$OPTARG"
		USEDEVEL="yes"
		coatjava_choice_count=$((coatjava_choice_count + 1))
		;;
	h)
		printHelp
		exit 0
		;;
	:)
		echo "Error: -$OPTARG requires an argument." >&2
		exit 1
		;;
	\?)
		echo "Error: unknown option -$OPTARG" >&2
		printHelp
		exit 1
		;;
	esac
done
shift $((OPTIND - 1))

if [[ $coatjava_choice_count -gt 1 ]]; then
	echo "Error: use at most one of -l, -t, or -g." >&2
	printHelp
	exit 1
fi

if [[ $# -ne 0 ]]; then
	echo "Error: unexpected argument: $1" >&2
	printHelp
	exit 1
fi

if [[ $USEDEVEL == "no" && -z "$COATJAVA_TAG" ]]; then
	echo "Fetching latest release from $REPO..."
	LATEST_RELEASE=$(curl -fsS "https://api.github.com/repos/$REPO/releases/latest" | jq -r .tag_name)
	if [[ -z "$LATEST_RELEASE" || "$LATEST_RELEASE" == "null" ]]; then
		echo "Error: could not determine latest coatjava release from $REPO." >&2
		exit 1
	fi
	COATJAVA_TAG="$LATEST_RELEASE"
	echo "Latest coatjava release from $REPO: $LATEST_RELEASE"
fi

if [[ $USEDEVEL == "yes" ]]; then
	echo "Requested Coatjava Repository: $githubRepo"
else
	echo "Requested Coatjava Tag: $COATJAVA_TAG"
fi

echo "START_INSTALL_COATJAVA $(date)" > "$log_file"
rm -rf coat*jar(N) jcsg*jar(N) vecmath*jar(N)

install_dir=coatjava
src_dir=coatjava_src

rm -rf "$install_dir" "$src_dir"

if [[ $USEDEVEL == "yes" ]]; then
	echo
	echo "Cloning $githubRepo and building coatjava"
	echo
	git -c advice.detachedHead=false clone "$githubRepo" "$src_dir"
else
	git -c advice.detachedHead=false clone -b "$COATJAVA_TAG" --recurse-submodules --shallow-submodules --depth 1 "$githubRepo" "$src_dir"
fi

cd "$src_dir"
parallel="-T1"
echo "Running coatjava build with options: --lfs --no-progress --nomaps $parallel" | tee -a "$log_file"
if ! ./build-coatjava.sh --lfs --no-progress --nomaps "$parallel" &>> "$log_file"; then
	echo "Error: coatjava build failed. Log:"
	cat "$log_file"
	exit 1
fi
cp coatjava/lib/clas/* ..
cp -r coatjava "../$install_dir"
echo "END_INSTALL_COATJAVA $(date)" >> "$log_file"
