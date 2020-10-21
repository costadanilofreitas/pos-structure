REM @echo off
call set_paths.bat
IF "%PYTHON_DIR%"=="" (
  set PYTHON_DIR=C:\Python27
)

IF "%GIT_DIR%"=="" (
set GIT_DIR=C:\Program Files\Git
)

IF "%NODE_DIR%"=="" (
set NODE_DIR=C:\Program Files\nodejs
)

set PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%GIT_DIR%;%GIT_DIR%\cmd\;%NODE_DIR%;%PATH%
REM git-bash -c "./make.sh"
