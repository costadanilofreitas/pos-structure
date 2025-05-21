call ..\..\scripts\python_path.bat
set PYTHONPATH=..\..\tests\;..\..\lib;..\..\src;..\..\dev_lib

python.exe run_all_unit_tests.py
