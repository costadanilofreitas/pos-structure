call ..\..\python_path.bat
set PYTHONPATH=..\..\test\;..\..\lib;..\..\src

python.exe run_all_unit_tests.py || exit 1
