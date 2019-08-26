@echo off

if [%1]==[] goto syntax

set MWAPP_CONFIG=%1
set PLATFORM=windows-x86
set BASEDIR="%CD%"
set BASEBINDIR=%BASEDIR%\mwsdk\%PLATFORM%
set MWAPP_DATADIR=%BASEDIR%\mwdatas\%MWAPP_CONFIG%

if not exist %MWAPP_DATADIR% goto :error1

:step1
if not exist %BASEDIR%\install goto :step2
rmdir /q /s install

:step2
mkdir install\genesis\bin
mkdir install\genesis\apache
mkdir install\genesis\python
mkdir install\bin
mkdir install\apache
mkdir install\python
mkdir install\data

:step3
mklink /D install\genesis\apache\windows-x86 %BASEBINDIR%\apache
if not errorlevel 0 goto :error2
mklink /D install\genesis\bin\windows-x86 %BASEBINDIR%\bin
if not errorlevel 0 goto :error2
mklink /D install\genesis\python\windows-x86 %BASEBINDIR%\python
if not errorlevel 0 goto :error2
mklink /D install\genesis\data %MWAPP_DATADIR%
echo 1 > install\genesis\.genversion
copy start.bat install\start.bat
copy stop.bat install\stop.bat
copy install\genesis\bin\windows-x86\*.* install\bin
goto :eof

:error1
echo "Data directory is invalid: %MWAPP_DATADIR%"
goto syntax

:error2
echo "Unable to create symbolic link"
goto syntax

:syntax
echo "Usage: build_environment.bat <data.[client]>"

:eof