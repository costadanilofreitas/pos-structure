#!/bin/bash
cd mwpos_server/data
if [ ! -d htdocs ]; then
  mkdir htdocs
fi
cd htdocs
if [ ! -d sui ]; then
  mkdir sui
fi
if [ ! -d kds ]; then
  mkdir kds
fi
if [ ! -d pickup ]; then
  mkdir pickup
fi
if [ ! -d prep ]; then
  mkdir prep
fi

cd ../../..

cd ../pos-structure/src/gui/3s-posui
rm package-lock.json
rm -rf node_modules
npm install
npm run build
cd lib
npm pack
cd ../..

cd 3s-widgets
rm package-lock.json
rm -rf node_modules
npm install
npm run build
cd lib
npm pack
cd ../..

cd newgui
sed -i 's,"posui": "git+https://git.mwneo.com/mw/posui.git#1.1.0","posui": "git+ssh://git@git.mwneo.com:mw/posui.git#1.1.0",g' package.json
rm package-lock.json
rm -rf node_modules
npm install
npm run build
rm -rf ../../../../applebees/mwpos_server/data/htdocs/sui/*
cp -r dist/* ../../../../applebees/mwpos_server/data/htdocs/sui
cd ..

cd pickup
sed -i 's,"posui": "git+https://git.mwneo.com/mw/posui.git#1.1.0","posui": "git+ssh://git@git.mwneo.com:mw/posui.git#1.1.0",g' package.json
rm package-lock.json
rm -rf node_modules
npm install
npm run build
rm -rf ../../../../applebees/mwpos_server/data/htdocs/pickup/*
cp -r dist/* ../../../../applebees/mwpos_server/data/htdocs/pickup
cd ..

cd ../../../components/prep
sed -i 's,"posui": "git+https://git.mwneo.com/mw/posui.git#1.1.0","posui": "git+ssh://git@git.mwneo.com:mw/posui.git#1.1.0",g' package.json
rm package-lock.json
rm -rf node_modules
npm install
npm run build
rm -rf ../../applebees/mwpos_server/data/htdocs/prep/*
cp -r dist/* ../../../applebees/mwpos_server/data/htdocs/prep
cd ..

cd kds
cp -r * ../../../applebees/mwpos_server/data/htdocs/kds
