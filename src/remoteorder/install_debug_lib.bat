rd /s /q debug_lib
call python_path.bat
python.exe -m pip install -r debug_requirements.txt -t debug_lib --extra-index-url=https://pip.e-deploy.com.br/
