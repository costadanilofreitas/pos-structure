rd /s /q node_modules\
rd /s /q lib\
del package-lock.json
cmd /C npm install
cmd /C npm run build
cd lib && cmd /C npm pack && cd ..
