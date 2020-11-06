@echo off

set PLATFORM=windows-x86
set BASEDIR="%CD%"

if exist %BASEDIR%\mwsdk goto :runhv
goto :EXIT

:rungenclient
set BASEBINDIR=%BASEDIR%
goto :setupenv

:runhv
set BASEBINDIR=%BASEDIR%\mwsdk\%PLATFORM%
goto :setupenv

:setupenv
set MWPOS_BIN=%BASEBINDIR%\bin
set APACHE_MODS=%BASEBINDIR%\apache\modules
set PYTHONHOME=%BASEBINDIR%\python
set DATADIR=%BASEDIR%\%MWAPP_CONFIG%
set HVLOGFILE=%DATADIR%\logs\hv.log
set HVMAXLOGFILES=5
set PATH=%PYTHONHOME%;%PYTHONHOME%\bin;%PYTHONHOME%\lib;%APACHE_MODS%;%PATH%

IF NOT EXIST %MWPOS_BIN%\hv.exe call :ERROR Could not find exexutable hv.exe.

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