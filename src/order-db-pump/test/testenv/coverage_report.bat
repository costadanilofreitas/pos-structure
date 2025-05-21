call ..\..\python_path.bat
set PYTHONPATH=..\..\test\;..\..\lib;..\..\src
set PYTHONPATH=%PYTHONPATH%;..\..\dev_lib

python.exe -m coverage run -m run_all_unit_tests
python.exe -m coverage xml -o reports\coverage.xml
python.exe -m coverage html
python.exe -m coverage report
