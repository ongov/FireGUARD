@echo off
SETLOCAL ENABLEEXTENSIONS
pushd %~dp0
echo Running FireSTARR
@rem call the parallel version and then the sequential one so this doesn't run while a previous version is running
python.exe runfire.py --check-maps %* >> ..\log_firestarr.txt
popd
echo Done
