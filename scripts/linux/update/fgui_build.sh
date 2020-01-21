#!/bin/bash
cd ../pos-structure/src/gui/newgui/
npm run build
rm -rf ../../../../applebees/mwpos_server/data/htdocs/sui/*
cp -r dist/* ../../../../applebees/mwpos_server/data/htdocs/sui
cd ../../../../applebees
