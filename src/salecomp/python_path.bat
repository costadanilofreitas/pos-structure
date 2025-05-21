set REL_PATH=..\..\mwsdk\windows-x86\python
pushd %REL_PATH%
set PYTHON_DIR=%CD%
popd
set PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%
