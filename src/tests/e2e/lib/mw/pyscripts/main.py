# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\main.py
import os
DEBUGGER = (os.environ.get('DEBUGGER') or 'false').lower() == 'true'
PYDEVPATH = os.environ.get('PYDEVPATH') or '/Users/amerolli/.p2/pool/plugins/org.python.pydev_5.9.2.201708151115/pysrc'

def main():
    if DEBUGGER:
        if os.path.exists(PYDEVPATH):
            import sys
            try:
                sys.path.index(PYDEVPATH)
            except:
                sys.path.append(PYDEVPATH)

            import pydevd
            pydevd.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True, suspend=False)
    import pyscripts
    pyscripts.__main()