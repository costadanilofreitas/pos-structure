cd ..\..
call python_path.bat
cd test\testenv
set PYTHONPATH=..\..\dev_lib;..\..\lib;..\..\test\;..\..\src;

python.exe run_all_unit_tests.py
