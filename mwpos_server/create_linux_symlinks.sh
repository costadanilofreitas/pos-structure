unlink genesis/apache/darwin-x86_64

unlink genesis/apache/linux-redhat-x86_64
ln -s ../../../mwappsdk/linux-redhat-x86_64/apache genesis/apache/linux-redhat-x86_64
unlink genesis/apache/linux-ubuntu-i686

unlink genesis/apache/linux-ubuntu-x86_64
ln -s ../../../mwappsdk/linux-ubuntu-x86_64/apache genesis/apache/linux-ubuntu-x86_64
unlink genesis/apache/windows-x86

unlink genesis/apache/windows-AMD64



unlink genesis/bin/darwin-x86_64

unlink genesis/bin/linux-redhat-x86_64
ln -s ../../../mwappsdk/linux-redhat-x86_64/bin genesis/bin/linux-redhat-x86_64
unlink genesis/bin/linux-ubuntu-i686

unlink genesis/bin/linux-ubuntu-x86_64
ln -s ../../../mwappsdk/linux-ubuntu-x86_64/bin genesis/bin/linux-ubuntu-x86_64
unlink genesis/bin/windows-x86

unlink genesis/bin/windows-AMD64



unlink genesis/python/darwin-x86_64

unlink genesis/python/linux-redhat-x86_64
ln -s ../../../mwappsdk/linux-redhat-x86_64/python genesis/python/linux-redhat-x86_64
unlink genesis/python/linux-ubuntu-i686

unlink genesis/python/linux-ubuntu-x86_64
ln -s ../../../mwappsdk/linux-ubuntu-x86_64/python genesis/python/linux-ubuntu-x86_64
unlink genesis/python/windows-x86

unlink genesis/python/windows-AMD64


unlink genesis/data/server
ln -s ../../../mwdatas/data.client/server genesis/data/server
