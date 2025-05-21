set REL_PYTHON_DIR=..\..\mwsdk\windows-x86\python
set PYTHON_DIR=
pushd %REL_PYTHON_DIR%
set PYTHON_DIR=%CD%
popd

set PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%