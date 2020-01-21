#!/bin/bash
cd ../pos-structure
git reset --hard
git clean -dxf
git checkout --
git checkout release/applebees/alphaville
git pull
cd src
git reset --hard
git clean -dxf
git checkout dev
git pull
cd ..
cd mwsdk
git reset --hard
git clean -dxf
git fetch --tag
git checkout v2.0.68
cd ..
cd components
git reset --hard
git clean -dxf
git checkout dev
git pull
