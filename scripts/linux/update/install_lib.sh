#!/bin/bash
cd ../pos-structure/components
cd new-production
rm -rf lib
../../mwsdk/linux-centos-x86_64/python/bin/python -m pip install -r requirements.txt -t lib --extra-index-url=http://pip.hmledp.com.br.s3-website.us-east-2.amazonaws.com/ --trusted-host pip.hmledp.com.br.s3-website.us-east-2.amazonaws.com

cd ../mebuhi
rm -rf lib
../../mwsdk/linux-centos-x86_64/python/bin/python -m pip install -r requirements.txt -t lib --extra-index-url=http://pip.hmledp.com.br.s3-website.us-east-2.amazonaws.com/ --trusted-host pip.hmledp.com.br.s3-website.us-east-2.amazonaws.com


cd ../../src/mobile-pos-printer
rm -rf lib
../../mwsdk/linux-centos-x86_64/python/bin/python -m pip install -r requirements.txt -t lib --extra-index-url=http://pip.hmledp.com.br.s3-website.us-east-2.amazonaws.com/ --trusted-host pip.hmledp.com.br.s3-website.us-east-2.amazonaws.com


cd ../sitef
../../mwsdk/linux-centos-x86_64/python/bin/python -m compileall .
cd ..
if [ -d pypkg ]; then
  rm -rf pypkg
fi
mkdir pypkg
cd sitef
rsync -zarv --include "*/" --include="*.pyc" --exclude="*" . ../pypkg
cd ../pypkg
mkdir lib
cp ../sitef/lib/* ./lib
zip -Dr sitef.pypkg *
cp sitef.pypkg ../../../applebees/mwpos_server/genesis/bin/windows-x86/
cp sitef.pypkg ../../../applebees/mwpos_server/genesis/bin/linux-centos-x86_64/
cd ..
rm -rf pypkg

cd satcomp
../../mwsdk/linux-centos-x86_64/python/bin/python -m compileall .
cd ..
if [ -d pypkg ]; then
  rm -rf pypkg
fi
mkdir pypkg
cd satcomp
rsync -zarv --include "*/" --include="*.pyc" --exclude="*" . ../pypkg
cd ../pypkg
mkdir dll
cp -r ../satcomp/dll/* ./dll
zip -Dr satcomp.pypkg *
cp satcomp.pypkg ../../../applebees/mwpos_server/genesis/bin/windows-x86/
cp satcomp.pypkg ../../../applebees/mwpos_server/genesis/bin/linux-centos-x86_64/
cd ..
rm -rf pypkg

cd edpcommon
../../mwsdk/linux-centos-x86_64/python/bin/python -m compileall .
cd ..
if [ -d pypkg ]; then
  rm -rf pypkg
fi
mkdir pypkg
cd edpcommon
rsync -zarv --include "*/" --include="*.pyc" --exclude="*" . ../pypkg
cd ../pypkg
zip -Dr edpcommon.pypkg *
cp edpcommon.pypkg ../../../applebees/mwpos_server/genesis/bin/windows-x86/
cp edpcommon.pypkg ../../../applebees/mwpos_server/genesis/bin/linux-centos-x86_64/
cd ..
rm -rf pypkg

cd maintenancecomp
../../mwsdk/linux-centos-x86_64/python/bin/python -m compileall .
cd ..
if [ -d pypkg ]; then
  rm -rf pypkg
fi
mkdir pypkg
cd maintenancecomp
rsync -zarv --include "*/" --include="*.pyc" --exclude="*" . ../pypkg
cd ../pypkg
zip -Dr maintenancecomp.pypkg *
cp maintenancecomp.pypkg ../../../applebees/mwpos_server/genesis/bin/windows-x86/
cp maintenancecomp.pypkg ../../../applebees/mwpos_server/genesis/bin/linux-centos-x86_64/
cd ..
rm -rf pypkg
