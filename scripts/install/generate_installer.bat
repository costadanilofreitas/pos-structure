if exist dist (
    rmdir /s /q "dist"
)

pyinstaller --onefile installEdeployPOS.py

if exist install (
    rmdir /s /q "install"
)
mkdir "install"
copy "dist" "install"
mkdir "install\pos_files"
copy "pos_files" "install/pos_files"
copy "configurations.txt" "install"

tar.exe -a -c -f install.zip install