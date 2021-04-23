if exist dist (
    rmdir /s /q "dist"
)

pyinstaller --onefile --icon="icon.png" installEdeployPOS.py

if exist install (
    rmdir /s /q "install"
)
mkdir "install"
xcopy "dist" "install" /E
mkdir "install\pos_files"
xcopy "pos_files" "install/pos_files" /E
copy "configurations.txt" "install"
mkdir "install\python"
xcopy "..\..\mwsdk\windows-x86\python" "install/python" /E

tar.exe -a -c -f install.zip install