@echo off
call loaddb.bat WXSHIELD.sql
call loaddb.bat HINDCAST.sql

REM Use current year for initialization
for /f "delims=" %%f in ('"powershell (Get-Date).Year"') do set YEAR=%%f
echo Initializing with year %YEAR%

call :loadYear %YEAR%
pushd ..
goto :end

:loadYear
call loaddb.bat DFOSS_%1 DFOSS.sql
call loaddb.bat WX_%101 WX.sql
call loaddb.bat WX_%102 WX.sql
call loaddb.bat WX_%103 WX.sql
call loaddb.bat WX_%104 WX.sql
call loaddb.bat WX_%105 WX.sql
call loaddb.bat WX_%106 WX.sql
call loaddb.bat WX_%107 WX.sql
call loaddb.bat WX_%108 WX.sql
call loaddb.bat WX_%109 WX.sql
call loaddb.bat WX_%110 WX.sql
call loaddb.bat WX_%111 WX.sql
call loaddb.bat WX_%112 WX.sql


:end
