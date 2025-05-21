call python_path.bat
set PYTHONPATH=dev_lib
python.exe -m pycodestyle --exclude=test/testenv/* src test