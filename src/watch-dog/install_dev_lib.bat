rd /s /q dev_lib
call python_path.bat
python.exe -m pip install -r dev_requirements.txt -t dev_lib --extra-index-url=http://nuget.e-deploy.com.br/pip/ --trusted-host nuget.e-deploy.com.br
