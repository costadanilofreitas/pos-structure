cd ..\..
call python_path.bat
cd test\testenv
set PYTHONPATH=..\..\lib;..\..\src
set PYTHONPATH=%PYTHONPATH%;..\..\test;..\..\dev_lib

python.exe -m coverage run -m pytest ..
python.exe -m coverage xml -o reports\coverage.xml
python.exe -m coverage html
python.exe -m coverage report
