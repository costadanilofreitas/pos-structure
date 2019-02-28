rmdir genesis\apache\darwin-x86_64

rmdir genesis\apache\linux-redhat-x86_64

rmdir genesis\apache\linux-ubuntu-i686

rmdir genesis\apache\linux-ubuntu-x86_64

rmdir genesis\apache\windows-x86
mklink /D genesis\apache\windows-x86 ..\..\..\mwappsdk\windows-x86\apache
rmdir genesis\apache\windows-AMD64
mklink /D genesis\apache\windows-AMD64 ..\..\..\mwappsdk\windows-x86\apache


rmdir genesis\bin\darwin-x86_64

rmdir genesis\bin\linux-redhat-x86_64

rmdir genesis\bin\linux-ubuntu-i686

rmdir genesis\bin\linux-ubuntu-x86_64

rmdir genesis\bin\windows-x86
mklink /D genesis\bin\windows-x86 ..\..\..\mwappsdk\windows-x86\bin
rmdir genesis\bin\windows-AMD64
mklink /D genesis\bin\windows-AMD64 ..\..\..\mwappsdk\windows-x86\bin


rmdir genesis\python\darwin-x86_64

rmdir genesis\python\linux-redhat-x86_64

rmdir genesis\python\linux-ubuntu-i686

rmdir genesis\python\linux-ubuntu-x86_64

rmdir genesis\python\windows-x86
mklink /D genesis\python\windows-x86 ..\..\..\mwappsdk\windows-x86\python
rmdir genesis\python\windows-AMD64
mklink /D genesis\python\windows-AMD64 ..\..\..\mwappsdk\windows-x86\python

rmdir genesis\data\server
mklink /D genesis\data\server ..\..\..\mwdatas\data.client\server
