#!/bin/bash
cd ../pos-structure
git checkout -- *
git pull
cd src
git checkout -- *
git pull
cd ..
cd components
git checkout -- *
git pull
