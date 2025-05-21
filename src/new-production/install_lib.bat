rd /s /q lib
call python_path.bat
python.exe -m pip install -r requirements.txt -t lib --extra-index-url=https://pip.e-deploy.com.br
