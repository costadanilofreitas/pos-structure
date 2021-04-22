if exist dist (
    rmdir /s /q "dist"
)

pyinstaller --onefile installEdeployPOS.py

if exist installEdeployPOS (
    rmdir /s /q "installEdeployPOS"
)
mkdir "installEdeployPOS"
copy "dist" "installEdeployPOS"
mkdir "installEdeployPOS\pos_files"
copy "pos_files" "installEdeployPOS/pos_files"
copy "configurations.txt" "installEdeployPOS"

tar.exe -a -c -f installEdeployPOS.zip installEdeployPOS