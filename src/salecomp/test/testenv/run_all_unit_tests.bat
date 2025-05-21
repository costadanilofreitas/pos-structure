cd ..\..
call python_path.bat
cd test\testenv
set PYTHONPATH=..\..\lib;..\..\src
set PYTHONPATH=%PYTHONPATH%;..\..\dev_lib;..\..\test

python.exe -m pytest .. || exit 1
