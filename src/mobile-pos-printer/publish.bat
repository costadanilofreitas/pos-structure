rd /s /q dist
mkdir dist
xcopy src\* dist /ed
xcopy lib\* dist /e
cd dist
dir /b *-info > infos.txt
for /f "tokens=*" %%a in (infos.txt) DO (
	rd /s /q %%a
)
del infos.txt
del /s *.pyc
rd /s /q setuptools
rd /s /q psycopg2\tests
rd /s /q sqlalchemy\testing
cd ..