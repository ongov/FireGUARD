del /s /q test\constant
call run.bat test test\constant all
python displaytest.py
call run.bat || (set ERRORLEVEL=1 && goto :end)
set ERRORLEVEL=0

:end
%COMSPEC% /C exit %ERRORLEVEL% >nul
