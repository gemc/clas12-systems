#!/usr/bin/env zsh

# Purpose: runs the geometry building scripts for the selected detector
# Assumptions:
# 1. the python sci-g main filename has the same name as the containing dir
# 2. the plugin directory is named 'plugin'

# Container run example:
# docker run -it --rm jeffersonlab/gemc:3.0-clas12 bash
# git clone http://github.com/gemc/clas12-systems /root/clas12-systems && cd /root/clas12-systems
# ./ci/build.sh -s ft/ft_cal

# load environment if we're on the container
TERM=xterm # source script use tput for colors, TERM needs to be specified
FILE=/etc/profile.d/jlab.sh

# notice the extra argument to the source command
test -f $FILE && source $FILE keepmine

Help()
{
	# Display Help
	echo
	echo "Syntax: build.sh [-h|s]"
	echo
	echo "Options:"
	echo
	echo "-h: Print this Help."
	echo "-s <System>: build geometry and plugin for <System>"
	echo
}

if [ $# -eq 0 ]; then
	Help
	exit
fi

while getopts ":hs:" option; do
   case $option in
      h) # display Help
         Help
         exit
         ;;
      s)
         detector=$OPTARG
         ;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit
         ;;
   esac
done

DetectorNotDefined () {
	echo "Detector is not set."
	Help
	exit
}

[[ -v detector ]] && echo "Building $detector" || DetectorNotDefined

DefineScriptName() {
	subDir=$(basename $detector)
	script="./"$subDir".py"
}


CreateAndCopyDetectorTXTs() {
	ls -ltrh ./
	echo
	echo Running $script
	$script
	ls -ltrh ./
	filesToCopy=$(git status -s | grep \? | awk '{print $2}' | grep -v \/ | grep \.txt)
	echo
	echo Moving $=filesToCopy to $GPLUGIN_PATH and cleaning up
	echo
	mv $=filesToCopy $GPLUGIN_PATH
	# cleaning up
	test -d __pycache__ && rm -rf __pycache__
	ls -ltrh ./
	echo
}

CompileAndCopyPlugin() {
	echo "Compiling plugin for "$detector
	echo
	cd plugin
	scons -j4 OPT=1
	echo Moving plugins to $GPLUGIN_PATH
	mv *.gplugin $GPLUGIN_PATH
	scons -c
	# cleaning up
	rm -rf .sconsign.dblite
	cd -
}

startDir=`pwd`
GPLUGIN_PATH=$startDir/systemsTxtDB
script=no

DefineScriptName $detector

echo
echo Building geometry for $detector. GPLUGIN_PATH is $GPLUGIN_PATH
echo
cd $detector
CreateAndCopyDetectorTXTs
test -d plugin && CompileAndCopyPlugin || echo "No plugin to build."

