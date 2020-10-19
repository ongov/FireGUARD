@echo off
SETLOCAL ENABLEEXTENSIONS
pushd ..\documentation\graphviz
set PATH=%CD%\bin;%CD%\lib;%PATH%
popd
..\documentation\doxygen\doxygen.exe gis.conf
