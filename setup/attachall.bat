SET SERVER=.\SQLEXPRESS

sqlcmd -S %SERVER% -E -Q "CREATE LOGIN [wx_readwrite] WITH PASSWORD=N'wx_r34dwr1t3p455w0rd!', DEFAULT_DATABASE=[master], DEFAULT_LANGUAGE=[us_english], CHECK_EXPIRATION=OFF, CHECK_POLICY=ON"
sqlcmd -S %SERVER% -E -Q "CREATE LOGIN [wx_readonly] WITH PASSWORD=N'wx_r34d0nly!', DEFAULT_DATABASE=[master], DEFAULT_LANGUAGE=[us_english], CHECK_EXPIRATION=OFF, CHECK_POLICY=ON"

call :attachyear 2016
call :attachyear 2017
call :attachyear 2018
call :attachyear 2019
call :attachyear 2020
call :doattach HINDCAST INPUTS
call :doattach WXSHIELD LOG


sqlcmd -S %SERVER% -E -Q "USE [WXSHIELD]; GRANT SELECT, INSERT, DELETE, UPDATE, EXECUTE ON SCHEMA::LOG TO wx_readwrite"
sqlcmd -S %SERVER% -E -Q "USE [WXSHIELD]; GRANT SELECT, INSERT, DELETE, UPDATE, EXECUTE ON SCHEMA::LOG TO wx_readonly"
sqlcmd -S %SERVER% -E -Q "USE [WXSHIELD]; GRANT SELECT, INSERT, DELETE, UPDATE, EXECUTE ON SCHEMA::INPUTS TO wx_readwrite"
sqlcmd -S %SERVER% -E -Q "USE [WXSHIELD]; GRANT SELECT, INSERT, DELETE, UPDATE, EXECUTE ON SCHEMA::INPUTS TO wx_readonly"
sqlcmd -S %SERVER% -E -Q "USE [HINDCAST]; GRANT SELECT, INSERT, DELETE, UPDATE, EXECUTE ON SCHEMA::HINDCAST TO wx_readwrite"
sqlcmd -S %SERVER% -E -Q "USE [HINDCAST]; GRANT SELECT ON SCHEMA::HINDCAST TO wx_readonly"

goto :end

:attachyear
call :doattach DFOSS_%1 INPUTS
call :doattach WX_%101 INPUTS
call :doattach WX_%102 INPUTS
call :doattach WX_%103 INPUTS
call :doattach WX_%104 INPUTS
call :doattach WX_%105 INPUTS
call :doattach WX_%106 INPUTS
call :doattach WX_%107 INPUTS
call :doattach WX_%108 INPUTS
call :doattach WX_%109 INPUTS
call :doattach WX_%110 INPUTS
call :doattach WX_%111 INPUTS
call :doattach WX_%112 INPUTS
goto :end

:doattach
sqlcmd -S %SERVER% -E -Q "CREATE DATABASE %1 ON (FILENAME = 'C:\Program Files\Microsoft SQL Server\MSSQL10_50.SQLEXPRESS\MSSQL\DATA\%1.mdf'), (FILENAME = 'C:\Program Files\Microsoft SQL Server\MSSQL10_50.SQLEXPRESS\MSSQL\DATA\%1_log.ldf') FOR ATTACH;"
sqlcmd -S %SERVER% -E -Q "USE [%1]; DROP USER [wx_readwrite]; CREATE USER [wx_readwrite] FOR LOGIN [wx_readwrite] WITH DEFAULT_SCHEMA=[%2]"
sqlcmd -S %SERVER% -E -Q "USE [%1]; DROP USER [wx_readonly]; CREATE USER [wx_readonly] FOR LOGIN [wx_readonly] WITH DEFAULT_SCHEMA=[%2]"
sqlcmd -S %SERVER% -E -Q "USE [%1]; GRANT SELECT, INSERT, DELETE, UPDATE, EXECUTE ON SCHEMA::%2 TO wx_readwrite"
sqlcmd -S %SERVER% -E -Q "USE [%1]; GRANT SELECT ON SCHEMA::%2 TO wx_readonly"

:end
 