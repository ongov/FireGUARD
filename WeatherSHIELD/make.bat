@echo off
SETLOCAL ENABLEEXTENSIONS
pushd %~dp0

pushd ..\documentation\graphviz
set PATH=%CD%\bin;%CD%\lib;%PATH%
popd
..\documentation\doxygen\doxygen.exe weathershield.conf

popd
