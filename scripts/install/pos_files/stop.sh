#!/bin/bash
HVPID=`ps -ef|grep -v "grep" |grep -v "hvmon" |grep  hv |awk ' { print $2 }'`

if [ "$HVPID" == "" ]; then
	echo "Unable to determine Hypervisor PID."
	exit 1
fi

OS=$(uname)
MARCH=$(uname -m)
BASEBINDIR=$(pwd)/mwsdk/windows-x86

if [ "$OS" == "Linux" ]; then
	LINUXFLAVOR=$(cat /etc/os-release | grep "^ID=" | cut -d "=" -f 2 | sed 's/"//g')
	BASEBINDIR=$(pwd)/mwsdk/linux-$LINUXFLAVOR-$MARCH
fi

if [ -d ./genesis ]; then
	BASEBINDIR=$(pwd)
elif [ ! -d $BASEBINDIR ]; then
	echo "Unable to determine correct MW:SDK binaries directory: $BASEBINDIR"
	exit 1
fi

BASEDIR=$(pwd)
MWAPP_DIR=$BASEBINDIR
MWAPP_PORT=14000
if [ -f $BASEDIR/$HVPID.hvpid ]; then
	MWAPP_PORT=`cat $BASEDIR/$HVPID.hvpid | cut -f 1`
fi

export DYLD_LIBRARY_PATH=$MWAPP_DIR/bin
export LD_LIBRARY_PATH=$DYLD_LIBRARY_PATH

UNAME=`id -u -n`
if [ ${UNAME} == "root" ]
then
	echo "Invalid user."
	exit 1
fi

pushd "$MWAPP_DIR/bin">/dev/null
./hv --tcp 127.0.0.1:$MWAPP_PORT --stop
echo -e "Stopping HyperVisor ..." 
while kill -0 "$HVPID" >>/dev/null 2>&1
do
	echo -e ".\c"
	sleep 1
done
echo  -e "\nHypervisor stopped"
rm -f $BASEDIR/$HVPID.hvpid
popd>/dev/null

