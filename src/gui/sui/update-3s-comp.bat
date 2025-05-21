rd /s /q node_modules\3s-posui\
rd /s /q node_modules\3s-widgets\
cd ..\3s-posui
cmd /C build.bat
cd ..\3s-widgets
cmd /C build.bat
cd ..\sui
del package-lock.json
cmd /C npm install
