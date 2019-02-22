@echo off

tasklist /FI "IMAGENAME eq genclient.exe" 2>NUL | find /I "genclient.exe" >NUL
if "%ERRORLEVEL%"=="0" (exit)
tasklist /FI "IMAGENAME eq hv.exe" 2>NUL | find /I "hv.exe" >NUL
if "%ERRORLEVEL%"=="0" (exit)

set DEBUGGER=false
set DEBUG=true
set PYDEVPATH=%CD%\pycharm-debug.egg
set MWPOS_BIN=%CD%\bin
set APACHE_MODS=%CD%\apache\modules
set PYTHONHOME=%CD%\python
set DATADIR=%CD%\data
set HVLOGFILE=%DATADIR%\logs\hv.log
set HVMAXLOGFILES=20
set PATH=%PYTHONHOME%;%PYTHONHOME%\bin;%PYTHONHOME%\lib;%PGSQLHOME%\bin;%PGSQLHOME%\lib;%APACHE_MODS%;%PATH%
set HVLOGLEVEL=63
set HVSTATS=1
IF "%NODEID%"=="" set NODEID=server

IF NOT EXIST "%MWPOS_BIN%\genclient.exe" call :ERROR Could not find hypervisor.

cd %MWPOS_BIN%
:: Run genclient
rem call :EXEC genclient --local ..\genesis --data "%DATADIR%" --notime 1 --force 1 --node %NODEID% 
hv.exe --service --data "%DATADIR%"
rem genclient.exe
goto EXIT

:: Function that executes a command and checks errorlevel
:EXEC
%*
IF NOT "%ERRORLEVEL%"=="0" call :ERROR "Error executing cmd: %*"
goto EXIT

:: Function that displays an error message and terminate the batch
:ERROR
echo.
echo %*
echo.
pause
rem exit

:EXIT
cd ..
