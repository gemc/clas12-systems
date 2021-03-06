#!/usr/bin/env zsh

# Purpose: runs the geometry building scripts for the selected detector
# Assumptions:
# 1. The python sci-g main python filename must match the containing dir name
# 2. The plugin directory, if existing, must be named 'plugin'

# Container run:
# docker run -it --rm jeffersonlab/gemc:3.0-clas12 sh
# git clone http://github.com/gemc/clas12-systems /root/clas12-systems && cd /root/clas12-systems
# git clone http://github.com/maureeungaro/clas12-systems /root/clas12-systems && cd /root/clas12-systems
# ./ci/build.sh -s ftof

if [[ -z "${G3CLAS12_VERSION}" ]]; then
	# load environment if we're on the container
	# notice the extra argument to the source command
	TERM=xterm # source script use tput for colors, TERM needs to be specified
	FILE=/etc/profile.d/jlab.sh
	test -f $FILE && source $FILE keepmine
else
  echo clas12-systems ci/build: environment already defined
fi

Help()
{
	# Display Help
	echo
	echo "Syntax: build.sh [-h|s|a]"
	echo
	echo "Options:"
	echo
	echo "-h: Print this Help."
	echo "-s <System>: build geometry and plugin for <System>"
	echo "-a: build geometry and plugin for all supported systems"
	echo
}

if [ $# -eq 0 ]; then
	Help
	exit 1
fi

# available systems
# ordered by z position
allSystems=(targets beamline ft fc ftof pcal)

while getopts ":has:" option; do
   case $option in
      h) # display Help
         Help
         exit
         ;;
      s)
         detector=$OPTARG
         ;;
      a)
         buildAll=yes
         ;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit 1
         ;;
   esac
done

CheckConditions () {
	if [[ ! -v buildAll ]]; then
		if [[ -v detector ]]; then
			echo "Building $detector"
		else
			echo "Detector is not set."
			Help
			exit 2
		fi
	fi
}

DefineScriptName() {
	system=$1
	subDir=$(basename $system)
	script="./"$subDir".py"
}


CreateAndCopyDetectorTXTs() {
	system=$1
	echo
	echo Running $script
	$script || { echo "Error when running $script" ; exit 1 }
	ls -ltrh ./
	subDir=$(basename $system)
	filesToCopy=$(ls | grep \.txt | grep "$subdir")
	echo
	echo Moving $=filesToCopy to $GPLUGIN_PATH and cleaning up
	echo
	mv $=filesToCopy $GPLUGIN_PATH
	# cleaning up
	test -d __pycache__ && rm -rf __pycache__
}

CompileAndCopyPlugin() {
	# getting number of available CPUS
	copt=" -j"`getconf _NPROCESSORS_ONLN`" OPT=1"
	echo
	echo Compiling $detector plugin with options: "$copt"
	echo
	cd plugin
	scons SHOWENV=1 SHOWBUILD=1 $copt
	gpls=$(ls *.gplugin)
	for gpl in $gpls;
	do
		ldresult=$( ld $gpl 2>&1 | grep undefined | wc -l )
		if [ $ldresult -ne 0 ]; then
			echo ld of gplugin $gpl returns undefined references
			ld $gpl
			echo
			exit 1
		fi
	done
	echo
	echo Moving plugins to $GPLUGIN_PATH
	mv *.gplugin $GPLUGIN_PATH
}

BuildSystem() {
	system=$1
	DefineScriptName $system
	echo
	echo Building geometry for $system. GPLUGIN_PATH is $GPLUGIN_PATH
	echo
	pwd
	cd $system
	CreateAndCopyDetectorTXTs $system
	test -d plugin && CompileAndCopyPlugin || echo "No plugin to build."
	echo $GPLUGIN_PATH content:
	ls -ltrh $GPLUGIN_PATH
	cd $startDir
}

BuildAllSystems() {
	for s in $allSystems
	do
		BuildSystem $s
	done
}

startDir=`pwd`
GPLUGIN_PATH=$startDir/systemsTxtDB
script=no

[[ -v buildAll ]] && BuildAllSystems || BuildSystem $detector

