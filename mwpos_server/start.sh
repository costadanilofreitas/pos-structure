#!/bin/bash

# Default values - change those on your environment
if [ "$(id -u)" == "0" ]; then
   echo "This script must NOT be run as root" 1>&2
   exit 1
fi

# Default values - change those on your environment
[ "$MWAPP_PORT" = "" ]  && MWAPP_PORT=14000

export DISPLAY=:0
DATADIR=../data/server/
pushd "$(dirname '$0')/bin">/dev/null
export LD_LIBRARY_PATH=$(pwd):$(pwd)/../pgsql/lib:$(pwd)/../python/lib
export PYTHONHOME=$(pwd)/../python
export HVLOGFILE=$DATADIR/logs/hv.log
# export HVLOGLEVEL=56
export HVMAXLOGFILES=120
nohup ./genclient --node server --local ../genesis --data $DATADIR --tcp "127.0.0.1:$MWAPP_PORT" --force 1 &
popd>/dev/null
