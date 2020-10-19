SETLOCAL ENABLEEXTENSIONS
pushd %~dp0

pushd ..\documentation\graphviz
set PATH=%CD%\bin;%PATH%
popd
call :domake FireSTARR
call :domake GIS
call :domake WeatherSHIELD
..\documentation\doxygen\doxygen.exe fireguard.conf
popd
goto :end

:domake
pushd ..\%1
..\documentation\doxygen\doxygen.exe %1.conf
popd

:end
