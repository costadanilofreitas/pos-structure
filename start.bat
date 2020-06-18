@echo off

SET CurDir=%CD%
cd datas\server\databases
if exist i18ncustom.db (
    del i18ncustom.db
)
cd %CurDir%

set MWAPP_NODE=server
set PLATFORM=windows-x86
set HVMAXLOGFILES=5
set HVLOGLEVEL=56
set BASEDIR=%CD%
set DEBUG=true

IF NOT EXIST %BASEDIR%\genesis call :ERROR Could not find 'genesis' in base dir.
IF NOT EXIST %BASEDIR%\mwsdk call :ERROR Could not find 'mwsdk' in base dir.

if exist %BASEDIR%\genesis goto :rungenclient
if exist %BASEDIR%\mwsdk goto :runhv
goto :EXIT

:rungenclient
set BASEBINDIR=%BASEDIR%
set MWDATASDIR=%BASEDIR%\..\datas
set EXECUTABLE=genclient.exe
goto :setupenv

:runhv
set BASEBINDIR=%BASEDIR%\mwsdk\%PLATFORM%
set MWDATASDIR=%BASEDIR%\datas
set EXECUTABLE=hv.exe
goto :setupenv

:setupenv
set MWPOS_BIN=%BASEBINDIR%\bin
set APACHE_MODS=%BASEBINDIR%\apache\modules
set PYTHONHOME=%BASEBINDIR%\python
set DATADIR=%MWDATASDIR%\
set HVLOGFILE=%DATADIR%\server\logs\hv.log
set PATH=%PYTHONHOME%;%PYTHONHOME%\bin;%PYTHONHOME%\lib;%APACHE_MODS%;%PATH%

IF NOT EXIST %MWPOS_BIN%\%EXECUTABLE% call :ERROR Could not find exexutable %EXECUTABLE%.

cd %MWPOS_BIN%
:: Run genclient
if [%EXECUTABLE%]==[genclient.exe] call :EXEC genclient.exe --local ..\genesis --notime 1 --force 1 --node %MWAPP_NODE% 
:: Run hv
if [%EXECUTABLE%]==[hv.exe] call :EXEC hv.exe --service --data "%DATADIR%\%MWAPP_NODE%"

:: Function that executes a command and checks errorlevel
:EXEC
%*
IF NOT "%ERRORLEVEL%"=="0" call :ERROR "Error executing cmd: %*"
goto :EXIT

:: Function that displays an error message and terminate the batch
:ERROR
echo.
echo %*
echo.

:EXIT
cd %BASEDIR%
goto :EOF

:SYNTAX
echo "Usage: start.bat <[client]> <node name>"

:EOF