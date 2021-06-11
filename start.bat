@echo off

tasklist /FI "IMAGENAME eq genclient.exe" 2>NUL | find /I "genclient.exe" >NUL
if "%ERRORLEVEL%"=="0" (exit)
tasklist /FI "IMAGENAME eq hv.exe" 2>NUL | find /I "hv.exe" >NUL
if "%ERRORLEVEL%"=="0" (exit)


set APP_NODE=server
set PLATFORM=windows-x86
set HVMAXLOGFILES=5
set HVLOGLEVEL=63
set BASEDIR=%CD%
set DEBUG=true

REM if exist %BASEDIR%\genesis goto :rungenclient
if exist %BASEDIR%\mwsdk goto :runhv
goto :EXIT

:rungenclient
set BASEBINDIR=%BASEDIR%
set DATADIR=%BASEDIR%\..\datas
set EXECUTABLE=genclient.exe
goto :setupenv

:runhv
set BASEBINDIR=%BASEDIR%\mwsdk\%PLATFORM%
set DATADIR=%BASEDIR%\datas
set EXECUTABLE=hv.exe
goto :setupenv

:setupenv
set POS_BIN=%BASEBINDIR%\bin
set APACHE_MODS=%BASEBINDIR%\apache\modules
set PYTHONHOME=%BASEBINDIR%\python
set DATADIR=%DATADIR%\
set HVLOGFILE=%DATADIR%\server\logs\hv.log
set PATH=%PYTHONHOME%;%PYTHONHOME%\bin;%PYTHONHOME%\lib;%APACHE_MODS%;%PATH%

IF NOT EXIST %POS_BIN%\%EXECUTABLE% call :ERROR Could not find executable %EXECUTABLE%.

cd %POS_BIN%
:: Run genclient
if [%EXECUTABLE%]==[genclient.exe] call :EXEC genclient.exe --local ..\genesis --data ..\data\server --notime 1 --force 1 --node %APP_NODE% 
:: Run hv
if [%EXECUTABLE%]==[hv.exe] call :EXEC hv.exe --service --data "%DATADIR%\%APP_NODE%"

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