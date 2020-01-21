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

cd mwpos_server
cd genesis

if [ -d apache ]; then
  rm -rf apache
fi
mkdir apache
if [ -d bin ]; then
  rm -rf bin
fi
mkdir bin
if [ -d python ]; then
  rm -rf python
fi
mkdir python

create_genesis_folder apache
create_genesis_folder python
create_genesis_folder bin
