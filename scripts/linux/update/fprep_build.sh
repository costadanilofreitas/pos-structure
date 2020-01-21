#!/bin/bash
cd ../pos-structure/components/prep/
npm run build
rm -rf ../../../applebees/mwpos_server/data/htdocs/prep/*
cp -r dist/* ../../../applebees/mwpos_server/data/htdocs/prep
cd ../../../applebees
