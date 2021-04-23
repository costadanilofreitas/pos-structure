if exist dist (
    rmdir /s /q "dist"
)
pyinstaller --onefile --name="edeployPOSInstaller.exe" --icon="pos_icon.ico" installEdeployPOS.py

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
tar.exe -a -c -f "edeploypos_windows.zip" install

tar.exe -a -c -f "edeploypos_linux.zip" "configurations.txt" "edeployPOS.x86_64.rpm"