call ..\..\python_path.bat
set PYTHONPATH=..\..\test\;..\..\lib;..\..\src
set PYTHONPATH=%PYTHONPATH%;..\..\dev_lib
set PYTHONPATH=%PYTHONPATH%;.

python.exe generate_summary_data.py
