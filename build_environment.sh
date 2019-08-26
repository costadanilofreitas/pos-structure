#!/bin/bash

MWAPP_CONFIG=$1

if [ "$MWAPP_CONFIG" == "" ]; then
	echo "SINTAXE: build_environment.sh <data.[client]>"
	exit 1
fi

OS=$(uname)
MARCH=$(uname -m)
BASEBINDIR=$(pwd)/mwsdk/windows-x86
PLATFORM=windows-x86
BASEDIR=$(pwd)
MWAPP_DATADIR=$BASEDIR/mwdatas/$MWAPP_CONFIG

if [ ! -d $MWAPP_DATADIR ]; then
	echo "Invalid data directory: $MWAPP_DATADIR"
	exit 1
fi

if [ "$OS" == "Darwin" ]; then
	PLATFORM=darwin-$MARCH
fi

if [ "$OS" == "Linux" ]; then
	LINUXFLAVOR=$(cat /etc/os-release | grep "^ID=" | cut -d "=" -f 2 | sed 's/"//g')
	PLATFORM=linux-$LINUXFLAVOR-$MARCH
fi

BASEBINDIR=$(pwd)/mwsdk/$PLATFORM

if [ ! -d $BASEBINDIR ]; then
	echo "Unable to determine correct MW:SDK binaries directory: $BASEBINDIR"
	exit 1
fi

if [ -d install ]; then
	rm -rf install
fi

mkdir -p install/genesis/bin
mkdir -p install/genesis/apache
mkdir -p install/genesis/python
mkdir -p install/genesis/pgsql
mkdir -p install/pgsql
mkdir -p install/python
mkdir -p install/apache
mkdir -p install/bin
mkdir -p install/data/bundles

ln -s $BASEBINDIR/bin install/genesis/bin/$PLATFORM
ln -s $BASEBINDIR/apache install/genesis/apache/$PLATFORM
ln -s $BASEBINDIR/python install/genesis/python/$PLATFORM
ln -s $BASEBINDIR/pgsql install/genesis/pgsql/$PLATFORM

if [ "$PLATFORM" == "linux-centos-x86_64" ]; then
	ln -s linux-centos-x86_64 install/genesis/bin/linux-redhat-x86_64
	ln -s linux-centos-x86_64 install/genesis/apache/linux-redhat-x86_64
	ln -s linux-centos-x86_64 install/genesis/python/linux-redhat-x86_64
	ln -s linux-centos-x86_64 install/genesis/pgsql/linux-redhat-x86_64
fi	



ln -s $MWAPP_DATADIR install/genesis/data

cp -R install/genesis/bin/$PLATFORM/* install/bin
cp install/genesis/data/server/bundles/*.gz install/data/bundles
cp install/genesis/data/server/bundles/loader.cfg install/data/bundles


echo "1" > install/genesis/.genversion
cp start.sh install/start.sh
cp stop.sh install/stop.sh


