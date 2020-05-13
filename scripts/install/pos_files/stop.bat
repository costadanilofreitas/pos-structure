@echo off

set PLATFORM=windows-x86
set BASEDIR="%CD%"

if exist %BASEDIR%\genesis goto :rungenclient
if exist %BASEDIR%\bin goto :runhv
goto :EXIT

:rungenclient
set BASEBINDIR=%BASEDIR%\bin
set DATADIR=%BASEDIR%\data
goto :setupenv

:runhv
set BASEBINDIR=%BASEDIR%\genesis\bin\%PLATFORM%
set DATADIR=%BASEDIR%\data
goto :setupenv

:setupenv
set MWPOS_BIN=%BASEBINDIR%
set APACHE_MODS=%BASEDIR%\apache\modules
set PYTHONHOME=%BASEDIR%\python
set DATADIR=%DATADIR%\
set HVLOGFILE=%DATADIR%\server\logs\hv.log
set HVMAXLOGFILES=5
set PATH=%PYTHONHOME%;%PYTHONHOME%\bin;%PYTHONHOME%\lib;%APACHE_MODS%;%PATH%

IF NOT EXIST %MWPOS_BIN%\hv.exe call :ERROR Could not find executable hv.exe.

cd %MWPOS_BIN%
:: Run hv
call :EXEC hv.exe --stop

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

:EOF