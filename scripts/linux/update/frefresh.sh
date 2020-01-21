#!/bin/bash
./fupdate_repos.sh
if [ ! -z $1 ] & [ $1 == 'with-gui' ];then
  ./fgui_build.sh
fi
if [ ! -z $1 ] & [ $1 == 'with-prep' ];then
  ./fprep_build.sh
fi
if [ ! -z $1 ] & [ $1 == 'with-all' ];then
  ./fgui_build.sh
  ./fprep_build.sh
fi
./genesis_update.sh
cd mwpos_server
./stop.sh
./start.sh
