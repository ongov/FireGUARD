setlocal enableextensions

pushd %~dp0
pushd sed\bin
SET PATH=%CD%;%PATH%
popd

SET DBNAME=%~n1
SET ORIG_NAME=%~n1
SET FROM_FILE=%1
if ""=="%2" goto :check_file
SET DBNAME=%1
SET ORIG_NAME=%~n2
SET FROM_FILE=%2

:check_file
echo Loading from file %FROM_FILE%

if not exist "%FROM_FILE%" goto :fail
  SET SERVER=.\SQLEXPRESS


:start
  echo Loading database %DBNAME%
  sqlcmd -S %SERVER% -E -Q "alter database [%DBNAME%] set single_user with rollback immediate"
  sqlcmd -S %SERVER% -E -Q "DROP DATABASE [%DBNAME%]"
  sqlcmd -S %SERVER% -E -Q "CREATE LOGIN [wx_readwrite] WITH PASSWORD=N'wx_r34dwr1t3p455w0rd!', DEFAULT_DATABASE=[master], DEFAULT_LANGUAGE=[us_english], CHECK_EXPIRATION=OFF, CHECK_POLICY=ON"
  sqlcmd -S %SERVER% -E -Q "CREATE LOGIN [wx_readonly] WITH PASSWORD=N'wx_r34d0nly!', DEFAULT_DATABASE=[master], DEFAULT_LANGUAGE=[us_english], CHECK_EXPIRATION=OFF, CHECK_POLICY=ON"
  @rem rename database references in input file
  @rem NOTE: assumes file name matches original database name
  sed "s/ DATABASE \[%ORIG_NAME%\]/ DATABASE \[%DBNAME%\]/g;s/USE \[%ORIG_NAME%\]/USE \[%DBNAME%\]/g;" %FROM_FILE% | sqlcmd -S %SERVER% -E
  popd
goto :done

:fail
  echo File %FROM_FILE% does not exist
:done


@rem Run as an admin
@rem ~ odbcconf.exe /a {CONFIGSYSDSN "SQL Server Native Client 10.0" "DSN=%DBNAME%|Description=%DBNAME%|SERVER=.\SQLEXPRESS|Database=%DBNAME%"}

@rem need to do:
@rem ~ pip install pyodbc