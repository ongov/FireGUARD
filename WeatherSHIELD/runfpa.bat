@echo off
SETLOCAL ENABLEEXTENSIONS
pushd %~dp0

for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set YMDDATE=%YYYY%%MM%%DD%
set HHMM=%HH%%Min%
set LOG_DIR=log
set LOG=%LOG_DIR%\log_fpa%YMDDATE%.txt

if not exist %LOG_DIR% mkdir %LOG_DIR%
echo Running FPA forecast update
python.exe fpaloader.py >> %LOG% 2>&1
echo Running DFOSS update
python.exe dfoss.py >> %LOG% 2>&1
echo Done
popd
