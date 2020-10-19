@echo off
SETLOCAL ENABLEEXTENSIONS
pushd %~dp0
echo Running FireSTARR for current perimeters
(python.exe runfire.py -c --check-maps %* && python runfire.py --clean) >> ..\log_firestarr_cur.txt
popd
echo Done
