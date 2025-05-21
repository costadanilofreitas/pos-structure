set PYTHONPATH=;..\..\common\;..\..\edpcommon\;..\lib;..\..\pyscripts_pypkg
set PYTHONPATH=%PYTHONPATH%;..\..\remoteorder\python\;..\..\remoteorder\lib
..\..\..\..\..\python\python.exe -m coverage erase
..\..\..\..\..\python\python.exe -m coverage run ..\tools\run_with_xml_output.py
..\..\..\..\..\python\python.exe -m coverage xml -i
