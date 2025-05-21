cd ..\..
call python_path.bat
cd test\testenv
set PYTHONPATH=..\..\dev_lib;..\..\lib;..\..\test\;..\..\src;

python.exe -m coverage run -m run_all_unit_tests
python.exe -m coverage xml -o reports\coverage.xml
python.exe -m coverage html
python.exe -m coverage report
