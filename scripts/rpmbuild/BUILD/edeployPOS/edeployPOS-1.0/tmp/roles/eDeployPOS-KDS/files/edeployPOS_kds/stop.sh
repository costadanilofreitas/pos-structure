#!/bin/bash

pushd "$(dirname $0)/bin">/dev/null
export LD_LIBRARY_PATH=$(pwd)
./hv --stop
popd>/dev/null
