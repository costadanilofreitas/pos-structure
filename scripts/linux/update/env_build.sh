#!/bin/bash
function create_genesis_folder() {
  cd $1
  create_platform_dirs
  copy_plataform_files $1
  cd ..
}

function create_platform_dirs() {
  if [ ! -d windows-x86 ]; then
    mkdir windows-x86
  fi
  if [ ! -d linux-centos-x86_64 ]; then
    mkdir linux-centos-x86_64
  fi
  if [ ! -L linux-centos-x86_64 ]; then
    ln -s ./linux-centos-x86_64/ linux-redhat-x86_64
  fi
}

function copy_plataform_files() {
  cd windows-x86
  cp -r ../../../../../pos-structure/mwsdk/windows-x86/$1/* .
  cd ..
  cd linux-centos-x86_64
  cp -r ../../../../../pos-structure/mwsdk/linux-centos-x86_64/$1/* .
  cd ..
}

function copy_component() {
  mkdir $1
  cd $1
  cp -r ../../../../pos-structure/src/$1/* .
  cd ..
}

if [ -d mwpos_server ]; then
    rm -rf mwpos_server
fi
if [ ! -d mwpos_server ]; then
  mkdir mwpos_server
fi
cd mwpos_server

if [ ! -d genesis ]; then
  mkdir genesis
fi
cd genesis

if [ ! -d apache ]; then
  mkdir apache
fi
if [ ! -d bin ]; then
  mkdir bin
fi
if [ ! -d data ]; then
  mkdir data
fi
if [ ! -d python ]; then
  mkdir python
fi

create_genesis_folder apache
create_genesis_folder python
create_genesis_folder bin

cd data
cp -r ../../../../pos-structure/mwdatas/data.client/* .
cd server/databases
rm *
cd ../..
cd ..

# genesis
echo "1">.genversion
cd ..

mkdir bin
cd bin
cp ../../../pos-structure/mwsdk/linux-centos-x86_64/bin/genclient .
cp ../../../pos-structure/mwsdk/linux-centos-x86_64/bin/libapriconv-1.so .
cp ../../../pos-structure/mwsdk/linux-centos-x86_64/bin/libsystools.so .
cp ../../../pos-structure/mwsdk/linux-centos-x86_64/bin/libaprutil-1.so.0.3.10 .
ln -s ./libaprutil-1.so.0.3.10 libaprutil-1.so.0
ln -s ./libaprutil-1.so.0.3.10 libaprutil-1.so
cp ../../../pos-structure/mwsdk/linux-centos-x86_64/bin/libzlib.so .
cp ../../../pos-structure/mwsdk/linux-centos-x86_64/bin/libtcputil.so .
cp ../../../pos-structure/mwsdk/linux-centos-x86_64/bin/libexpat.so .
cp ../../../pos-structure/mwsdk/linux-centos-x86_64/bin/libapr-1.so.0.4.2 .
ln -s libapr-1.so.0.4.2 libapr-1.so
ln -s libapr-1.so.0.4.2 libapr-1.so.0
cp ../../../pos-structure/mwsdk/linux-centos-x86_64/bin/libmsgbus.so .
cp ../../../pos-structure/mwsdk/linux-centos-x86_64/bin/libscew.so .
cd ..

mkdir data
mkdir data/logs

mkdir src
cd src
copy_component chatcontroller
copy_component dailygoals
copy_component edpcommon
copy_component edpreports
copy_component edpscripts
copy_component fiscalwrapper
copy_component kdsmonitor
copy_component mobile-pos-printer
copy_component ntaxcalc
copy_component remoteorder
copy_component remoteorderapi
copy_component tablemgr
cd ..

cp ../../pos-structure/start.sh .
chmod +x start.sh
cp ../../pos-structure/stop.sh .
chmod +x stop.sh
