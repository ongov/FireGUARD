@echo off
SETLOCAL ENABLEEXTENSIONS
call make.bat
set OUTPUT_FOLDER=test
SET CALL_WHAT=start pythonw
del /s /q %OUTPUT_FOLDER%
set ERRORLEVEL=0
set EXTRA=--year 2018
call :runfires

set EXTRA=--year 2019
call :runfire RED024

goto :runNOR072
:runfires
FOR %%i IN (
    APK005
    PAR003
    RED100
    SLK007
    RED097
    SLK057
    THU001
) do call :runfire %%i
goto :end

:runNOR072
set CALL_WHAT=python
set EXTRA=--date 2018-07-20 --ffmc 92 --dmc 59 --dc 318
call :runfire NOR072

@rem ~ python runfire.py -d --folder test --clean
@rem ~ python runfire.py -d --folder test --fire APK005 --year 2018 --check-maps
@rem ~ python runfire.py -d --folder test --fire PAR003 --year 2018 --check-maps
@rem ~ python runfire.py -d --folder test --fire RED100 --year 2018 --check-maps
@rem ~ python runfire.py -d --folder test --fire SLK007 --year 2018 --check-maps
@rem ~ python runfire.py -d --folder test --fire RED097 --year 2018 --check-maps
@rem ~ python runfire.py -d --folder test --fire SLK057 --year 2018 --check-maps
@rem ~ python runfire.py -d --folder test --fire THU001 --year 2018 --check-maps
@rem ~ python runfire.py -d --folder test --fire RED024 --year 2019 --check-maps
@rem ~ python runfire.py -d --folder test --clean
@rem ~ python runfire.py -d --folder test --fire NOR072 --date 2018-07-20 --ffmc 92 --dmc 59 --dc 318 --check-maps

@rem ~ Release\firestarr.exe test/output/APK/APK005/2018-07-02_0935 2018-07-02 45.7274 -78.6635 09:35
@rem ~ Release\firestarr.exe test/output/PAR/PAR003/2018-05-14_1450 2018-05-14 44.9039 -79.6604 14:50
@rem ~ Release\firestarr.exe test/output/RED/RED100/2018-07-17_1528 2018-07-17 50.7742 -94.4005 15:28
@rem ~ Release\firestarr.exe test/output/SLK/SLK007/2018-05-21_1921 2018-05-21 51.219 -90.2008 19:21
@rem ~ Release\firestarr.exe test/output/RED/RED097/2018-07-17_1523 2018-07-17 51.1192 -94.7553 15:23
@rem ~ Release\firestarr.exe test/output/SLK/SLK057/2018-07-08_1720 2018-07-08 52.7569 -89.0235 17:20 --size 100
@rem ~ Release\firestarr.exe test/output/THU/THU001/2018-04-23_2017 2018-04-23 48.3568 -89.2851 20:17
@rem ~ Release\firestarr.exe test/output/RED/RED024/2019-06-15_1641 2019-06-15 52.5163 -94.3683 16:41 --size 2
@rem ~ Release\firestarr.exe test/output/NOR/NOR072/2018-07-20_0000 2018-07-20 47.3711 -80.4615 00:00 --perim C:/FireGUARD/FireSTARR_dev/test/output/NOR/NOR072/2018-07-20_0000/NOR072.tif --ffmc 92 --dmc 59 --dc 318

@rem do this last so that the checks it has at the end apply
call dotest.bat || (set ERRORLEVEL=1 && goto :end)
goto :end

:runfire
@rem HACK: use %* but put fire first so we can add arguments
@echo on
%CALL_WHAT% runfire.py -d --folder %OUTPUT_FOLDER% --fire %* %EXTRA% || (set ERRORLEVEL=1 && goto :end)
@echo off
set ERRORLEVEL=0

:end
%COMSPEC% /C exit %ERRORLEVEL% >nul
