@echo off
SETLOCAL ENABLEEXTENSIONS
IF DEFINED ENV_IS_SET goto :build
SET ENV_IS_SET=1
pushd "C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\"
call VC\Auxiliary\Build\vcvarsx86_amd64.bat
popd

:build
SET Platform=
msbuild /p:Configuration=Release /m
