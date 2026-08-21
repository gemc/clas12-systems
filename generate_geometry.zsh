#!/usr/bin/env zsh

emulate -L zsh
setopt errexit nounset pipe_fail

usage() {
	cat <<'EOF'
Usage: generate_geometry.zsh [-f sqlite|ascii] [-s "SYSTEM ..."] [-p PREFIX]

Run the selected subsystem geometry scripts and collect their output under the
experiments directory.

Options:
  -f, --factory FACTORY   Output factory: sqlite (default) or ascii.
  -s, --systems SYSTEMS   Space- or comma-separated systems.
                          Default: dc ftof ec pcal ltcc
  -p, --prefix PREFIX     Installation prefix. Defaults to the prefix configured
                          in build/.
  --no-install            Generate experiments/ without installing it.
  -h, --help              Show this help message.

SQLite output is written to experiments/gemc.sqlite. ASCII files are written
to experiments/SYSTEM/ for each selected system. Mapped STL directories are
copied to experiments/SYSTEM/STL_DIRECTORY/ for either factory.
The completed experiments directory is copied to PREFIX/experiments unless
--no-install is used.
EOF
}

factory=sqlite
systems=(dc ft ftof ec ltcc pcal)
prefix=
install_experiments=1

# Space-separated geometry_src/<system> subdirectories containing runtime STL assets. Keep this map
# explicit so adding CAD to another detector only requires adding its directory name here.
typeset -A stl_directories=(
	ltcc stls
)

while (( $# > 0 )); do
	case "$1" in
		-f|--factory)
			if (( $# < 2 )); then
				print -u2 "Error: $1 requires a factory."
				usage >&2
				exit 2
			fi
			factory=$2
			shift 2
			;;
		--factory=*)
			factory=${1#*=}
			shift
			;;
		-s|--systems)
			if (( $# < 2 )); then
				print -u2 "Error: $1 requires a system list."
				usage >&2
				exit 2
			fi
			selection=${2//,/ }
			systems=(${=selection})
			shift 2
			;;
		--systems=*)
			selection=${${1#*=}//,/ }
			systems=(${=selection})
			shift
			;;
		-p|--prefix)
			if (( $# < 2 )); then
				print -u2 "Error: $1 requires an installation prefix."
				exit 2
			fi
			prefix=$2
			shift 2
			;;
		--prefix=*)
			prefix=${1#*=}
			shift
			;;
		--no-install)
			install_experiments=0
			shift
			;;
		-h|--help)
			usage
			exit 0
			;;
		*)
			print -u2 "Error: unknown option: $1"
			usage >&2
			exit 2
			;;
	esac
done

if [[ $factory != sqlite && $factory != ascii ]]; then
	print -u2 "Error: factory must be 'sqlite' or 'ascii', not '$factory'."
	exit 2
fi

if (( ${#systems} == 0 )); then
	print -u2 "Error: select at least one subsystem."
	exit 2
fi

repo_dir=${0:A:h}
experiments_dir=$repo_dir/experiments
geometry_dir=$repo_dir/geometry_src
python_command=${PYTHON:-python3}

if ! command -v "$python_command" >/dev/null 2>&1; then
	print -u2 "Error: Python command not found: $python_command"
	exit 1
fi

if (( install_experiments )) && [[ -z $prefix ]]; then
	if ! command -v meson >/dev/null 2>&1 || [[ ! -d $repo_dir/build/meson-info ]]; then
		print -u2 "Error: cannot infer the install prefix from build/."
		print -u2 "Configure Meson first, pass --prefix, or use --no-install."
		exit 1
	fi

	prefix=$(
		meson introspect --buildoptions "$repo_dir/build" |
			"$python_command" -c \
			'import json, sys; print(next(o["value"] for o in json.load(sys.stdin) if o["name"] == "prefix"))'
	)
fi

typeset -a selected_systems
typeset -a ascii_output_dirs
typeset -A seen_systems

if [[ $factory == sqlite ]]; then
	# The database is a generated aggregate. Rebuild it so removed systems, variations, or volumes cannot
	# survive from an earlier invocation.
	rm -f "$experiments_dir/gemc.sqlite"
fi

copy_stl_directories() {
	local system=$1
	local detector_dir=$geometry_dir/$system
	local stl_dir source_dir target_dir
	typeset -a stl_files

	if (( ! ${+stl_directories[$system]} )); then
		return
	fi

	for stl_dir in ${=stl_directories[$system]}; do
		source_dir=$detector_dir/$stl_dir
		if [[ ! -d $source_dir ]]; then
			print -u2 "Error: mapped STL directory not found for subsystem '$system': $source_dir"
			exit 2
		fi

		stl_files=("$source_dir"/*.stl(N))
		if (( ${#stl_files} == 0 )); then
			print -u2 "Error: mapped STL directory contains no .stl files: $source_dir"
			exit 2
		fi

		target_dir=$experiments_dir/$system/$stl_dir
		rm -rf "$target_dir"
		mkdir -p "$target_dir"
		cp $stl_files "$target_dir/"
		print "Copied ${#stl_files} STL files for $system to $target_dir"
	done
}

for system in $systems; do
	if (( ${+seen_systems[$system]} )); then
		continue
	fi

	geometry_script=$geometry_dir/$system/$system.py
	if [[ ! -f $geometry_script ]]; then
		print -u2 "Error: geometry script not found for subsystem '$system': $geometry_script"
		exit 2
	fi

	seen_systems[$system]=1
	selected_systems+=($system)
done

for system in $selected_systems; do
	detector_dir=$geometry_dir/$system
	geometry_script=$detector_dir/$system.py
	print "Generating $system geometry with the $factory factory..."

	if [[ $factory == sqlite ]]; then
		(
			cd "$detector_dir"
			"$python_command" "$geometry_script" -f sqlite -sql "$experiments_dir/gemc.sqlite"
		)
	else
		output_dir=$experiments_dir/$system
		mkdir -p "$output_dir"
		ascii_output_dirs+=($output_dir)
		(
			cd "$output_dir"
			"$python_command" "$geometry_script" -f ascii
		)
	fi

	copy_stl_directories "$system"
done

if [[ $factory == sqlite ]]; then
	print "Geometry database: $experiments_dir/gemc.sqlite"
else
	print "ASCII geometry directories: ${(j: :)ascii_output_dirs}"
fi

if (( install_experiments )); then
	if [[ -z $prefix || $prefix != /* || $prefix == / ]]; then
		print -u2 "Error: installation prefix must be an absolute path other than '/': $prefix"
		exit 2
	fi

	install_dir=$prefix/experiments
	if [[ ${install_dir:A} == ${experiments_dir:A} ]]; then
		print -u2 "Error: installation directory cannot be the source experiments directory."
		exit 2
	fi

	rm -rf "$install_dir"
	mkdir -p "$prefix"
	cp -R "$experiments_dir" "$prefix/"
	print "Installed experiments directory: $install_dir"
fi
