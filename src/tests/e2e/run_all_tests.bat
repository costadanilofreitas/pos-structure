call python_path.bat
set PLATFORM=windows-x86
set PYTHONPATH=lib;src;util;..\..\..\mwsdk\windows-x86\bin\common.pypkg
set BIN_PATH=;..\..\..\mwsdk\windows-x86\bin
set DATA_PATH=;..\..\..\mwdatas\data.client\server
for /f "tokens=*" %%G in ('dir /b /a:d src') do python -m behave src/%%G