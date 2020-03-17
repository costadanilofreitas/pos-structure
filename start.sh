#!/bin/bash
if [ -z "$MWAPP_CONFIG" ]
then
	export MWAPP_CONFIG=data.client
	echo "Using default MWAPP node: $MWAPP_CONFIG"
fi

if [ -z "$MWAPP_NODE" ]
then
	export MWAPP_NODE=server
	echo "Using default MWAPP node: $MWAPP_NODE"
fi

if [ -z "$MWAPP_PORT" ]
then
	export MWAPP_PORT=14000
	echo "Using default MWAPP port: $MWAPP_PORT"
fi

OS=$(uname)
MARCH=$(uname -m)
BASEBINDIR=$(pwd)/mwsdk/windows-x86
EXECUTABLE=hv
NOHUP='nohup'

if [ "$OS" == "Darwin" ]; then
	BASEBINDIR=$(pwd)/mwsdk/darwin-$MARCH
	NOHUP=''
fi

if [ "$OS" == "Linux" ]; then
	LINUXFLAVOR=$(cat /etc/os-release | grep "^ID=" | cut -d "=" -f 2 | sed 's/"//g')
	BASEBINDIR=$(pwd)/mwsdk/linux-$LINUXFLAVOR-$MARCH
fi

if [ -d ./genesis ]; then
	BASEBINDIR=$(pwd)
	EXECUTABLE=genclient
elif [ ! -d $BASEBINDIR ]; then
	echo "Unable to determine correct MW:SDK binaries directory: $BASEBINDIR"
	exit 1
fi

export MWAPP_DIR=$BASEBINDIR

if [ ! -f $MWAPP_DIR/bin/$EXECUTABLE ]; then
	echo "Unable to find executable: $MWAPP_DIR/bin/$EXECUTABLE"
	exit 1
fi

export MWAPP_BIN=$MWAPP_DIR/bin
export PYTHONHOME=$MWAPP_DIR/python
export DYLD_LIBRARY_PATH=$MWAPP_BIN:$PYTHONHOME/lib
export LD_LIBRARY_PATH=$DYLD_LIBRARY_PATH

if [ "$EXECUTABLE" == "genclient" ]; then
	export MWAPP_DATADIR=$(pwd)/datas
	export HVLOGFILE=$MWAPP_DATADIR/logs/hv.log
	export HVMAXLOGFILES=5
else
	export MWAPP_DATADIR=$(pwd)/datas/$MWAPP_NODE
	export HVLOGFILE=$MWAPP_DATADIR/logs/hv.log
	export HVMAXLOGFILES=5
	export HVLOGLEVEL=63
	if [ ! -d $MWAPP_DATADIR ]
	then
		echo "Invalid data/node directory: $MWAPP_DATADIR"
		echo "Please verify if MWAPP_NODE are correct: MWAPP_NODE=$MWAPP_NODE"
		exit 1
	fi

	if [ ! -f $MWAPP_DATADIR/bundles/loader.cfg ]
	then
		echo "Invalid data/node directory. Base loader.cfg file was not found: $MWAPP_DATADIR/bundles/loader.cfg"
		echo "Please verify if MWAPP_NODE are correct: MWAPP_NODE=$MWAPP_NODE"
		exit 1
	fi

	if [ ! -f $MWAPP_DATADIR/bundles/license.gz ]
	then
		echo "Invalid data/node directory. License file was not found under $MWAPP_DATADIR/bundles directory."
		echo "Please verify if MWAPP_NODE are correct: MWAPP_NODE=$MWAPP_NODE"
		exit 1
	fi
fi

UNAME=`id -u -n`
if [ ${UNAME} == "root" ]
then
	echo "Invalid user"
	exit 1
else
	if [ "$EXECUTABLE" == "genclient" ]; then
		BASEDIR=$(pwd)
		rm -f $BASEDIR/*.hvpid
		pushd "$MWAPP_BIN">/dev/null
		nohup ./genclient --local ../genesis --notime 1 --force 1 --node $MWAPP_NODE --tcp 127.0.0.1:$MWAPP_PORT>/dev/null 2>&1 &
		popd>/dev/null
	else
		BASEDIR=$(pwd)
		rm -f $BASEDIR/*.hvpid
		pushd "$MWAPP_BIN">/dev/null
		$NOHUP ./hv --service --data $MWAPP_DATADIR --tcp 127.0.0.1:$MWAPP_PORT>/dev/null 2>&1 &
		echo "$MWAPP_PORT	$MWAPP_DATADIR" > $BASEDIR/$!.hvpid
		popd>/dev/null
	fi
fi

