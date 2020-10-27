@echo off
setlocal enableextensions
pushd %~dp0
SET LOCAL_DIR=%CD%
SET DOWNLOAD_DIR=%LOCAL_DIR%\download
mkdir %DOWNLOAD_DIR%

net session >nul 2>&1
IF NOT %ERRORLEVEL%==0 echo Must run as administrator in elevated command prompt && goto :end

echo NOTE: By using this software you agree to the terms of all products installed or used by it
PAUSE

SET HAVEPROXY=
SET EXTRA_USERS=%*
SET SQLINSTALL=SQLEXPRWT_x86_ENU.exe
SET SQLDOWNLOAD=http://download.microsoft.com/download/0/4/B/04BE03CD-EAF3-4797-9D8D-2E08E316C998

SET ISWIN10=
(wmic os get version | findstr /I ^^10.>NUL) && set ISWIN10=1

@rem this is the same for 32 and 64 bit
SET SQLBINPATH=C:\Program Files\Microsoft SQL Server\100\Tools\Binn
IF DEFINED ProgramFiles(x86) (
    goto set64bit
)
goto haveArchitecture

:set64bit
SET SQLINSTALL=SQLEXPRWT_x64_ENU.exe

:haveArchitecture
@rem figure out who's installing this so we know what environment we're in
for /f "tokens=*" %%a in ('whoami') do set USERS="%%a"

whoami | findstr cihs\\.*\.admin\.cihs >nul && goto :isCIHS
goto :haveUsers

:isCIHS
for /f "tokens=*" %%a in ('echo ontario\%USERS:~6,-12%') do set BASE_USER="%%a"
set USERS=%USERS% %BASE_USER%

:haveUsers

@rem Override proxy settings by uncommenting and changing this
@rem SET proxyHost=
@rem SET proxyPort=
@rem goto :doneproxy

@rem Use a variable for the extra java arguments so we can set a proxy if needed
SET ARGS=

@rem comment this out if you are manually setting a proxy above
echo Checking for proxy
set HTTP_PROXY=
@rem check for a registry key setting the proxy to the standard MNR proxy and if it's there then
@rem    we see if we can resolve its IP address and use the known proxy settings from that .pac file
@rem    when we start the application
@rem    otherwise we just call the app with no proxy set and it should work
for /f "tokens=3 delims=; " %%a in ('REG QUERY "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings" /v AutoConfigURL') do set PAC_FILE="%%a"
IF NOT DEFINED PAC_FILE goto :doneproxy
set PAC_FILE=%PAC_FILE:"=%
@rem if this doesn't exist then there's no autoconfigured proxy
IF "" EQU "%PAC_FILE%" goto :doneproxy

@rem get the server name out of the proxy
set PAC_SERVER=%PAC_FILE:http://=%
@rem find a : in the address
set "str_end=%PAC_SERVER:*:=%"
@rem remove everything after that
call set PAC_SERVER=%%PAC_SERVER:%str_end%=%%
@rem remove the :
set PAC_SERVER=%PAC_SERVER::=%
@rem if we can't resolve the server then don't use it (still use it even if we can't ping)
ping -n 1 -w 0 -a %PAC_SERVER% | findstr Pinging >NUL || (echo Cannot resolve PAC file server %PAC_SERVER% && goto :doneproxy)
@rem download the .pac file
PowerShell (new-object System.Net.WebClient).DownloadFile('%PAC_FILE%', 'proxy.pac') 2>NUL|| (echo Cannot reach proxy && goto :doneproxy)
@rem this relies on knowing that our proxies use as a specific port

for /f "tokens=*" %%a in ('type proxy.pac ^| findstr PROXY') do call :tryProxy %%a

goto :doneproxy

:tryProxy
@rem if this is defined then we already ran everything
IF DEFINED HAVEPROXY goto :end
set test=%1
set test=%test:"=%
if "" == "%test%" goto :doneproxy
set TEST_PROXY=%test:PROXY =%
if "%TEST_PROXY%" == "%test%" goto :doShift
set TEST_PROXY=%TEST_PROXY:;=%
@rem find a : in the address
set "str_end=%TEST_PROXY:*:=%"
@rem remove everything after that
call set TEST_PROXY=%%TEST_PROXY:%str_end%=%%
@rem remove the :
set TEST_PROXY=%TEST_PROXY::=%
SET proxyHost=%TEST_PROXY%
set proxyHost=%proxyHost: =%
SET proxyPort=%str_end%
set proxyPort=%proxyPort: =%
ping -n 1 -w 0 -a %TEST_PROXY% | findstr Pinging >NUL && goto :haveproxy
@rem didn't find it so clear it
set TEST_PROXY=
goto :end
:doShift
SHIFT
IF NOT DEFINED HTTP_PROXY goto :tryProxy


:haveproxy
SET HTTP_PROXY=http://%proxyHost%:%proxyPort%
echo Detected proxy %proxyHost% on port %proxyPort%
SET ARGS=-Dhttp.proxyHost=%proxyHost% -Dhttp.proxyPort=%proxyPort% -Dhttps.proxyHost=%proxyHost% -Dhttps.proxyPort=%proxyPort%

:doneproxy
@rem reset this so we don't get an error message from the .vbs if we didn't find a proxy
SET ERRORLEVEL=0
IF DEFINED HTTP_PROXY SET HTTPS_PROXY=%HTTP_PROXY%
IF DEFINED HTTP_PROXY set HTTPS_PROXY=%HTTPS_PROXY:http://=https://%
SET HAVEPROXY=1

@echo Downloading required files
call :ensure_file "%SQLDOWNLOAD%/%SQLINSTALL%" "%SQLINSTALL%"
call :ensure_file "https://www.python.org/ftp/python/2.7.18/python-2.7.18.msi" "python-2.7.18.msi"
call :ensure_file "http://download.microsoft.com/download/9/5/A/95A9616B-7A37-4AF6-BC36-D6EA96C8DAAE/dotNetFx40_Full_x86_x64.exe" "dotNetFx40_Full_x86_x64.exe"
SET PHP=php-7.4.11-nts-Win32-vc15-x64.zip
set PHPDIR=c:\php
call :ensure_file "https://windows.php.net/downloads/releases/%PHP%" "%PHP%"
call :ensure_file "https://go.microsoft.com/fwlink/?linkid=2120362" "SQLSRV58.EXE"
call :ensure_file "https://go.microsoft.com/fwlink/?linkid=2120137" "msodbcsql.msi"
SET DOXYGEN_ZIP=doxygen-1.8.20.windows.x64.bin.zip
call :ensure_file "http://doxygen.nl/files/%DOXYGEN_ZIP%" %DOXYGEN_ZIP%
SET DIA_ZIP=dia_0.97.2_win32.zip
call :ensure_file "https://sourceforge.net/projects/dia-installer/files/dia/0.97.2/%DIA_ZIP%/download" %DIA_ZIP%
SET GV_ZIP=graphviz-2.44.1-win32.zip
call :ensure_file https://www2.graphviz.org/Packages/stable/windows/10/msbuild/Release/Win32/%GV_ZIP% %GV_ZIP%
SET PDFSIZEOPT_ZIP=pdfsizeopt_win32exec-v6.zip
call :ensure_file https://github.com/pts/pdfsizeopt/releases/download/2017-09-02w/%PDFSIZEOPT_ZIP% %PDFSIZEOPT_ZIP%
SET CHROME_ZIP=chromedriver_win32.zip
call :ensure_file https://chromedriver.storage.googleapis.com/86.0.4240.22/%CHROME_ZIP% %CHROME_ZIP%
SET WGRIB_ZIP=wgrib2-v0.1.9.4-bin-i686-pc-cygwin.zip
call :ensure_file https://sourceforge.net/projects/opengrads/files/wgrib2/0.1.9.4/%WGRIB_ZIP%/download %WGRIB_ZIP%
SET _7Z_ZIP=7za920.zip
call :ensure_file https://www.7-zip.org/a/%_7Z_ZIP% %_7Z_ZIP%
SET CYGWIN_TAR=cygwin-3.1.7-1.tar
SET CYGWIN_XZ=%CYGWIN_TAR%.xz
call :ensure_file http://mirror.csclub.uwaterloo.ca/cygwin/x86/release/cygwin/%CYGWIN_XZ% %CYGWIN_XZ%
SET SED_ZIP=sed-4.0.7-bin.zip
call :ensure_file https://sourceforge.net/projects/gnuwin32/files//sed/4.0.7/%SED_ZIP%/download %SED_ZIP%
SET LIBINTL_ZIP=libintl-0.11.5-2-bin.zip
call :ensure_file https://sourceforge.net/projects/gnuwin32/files/libintl/0.11.5-2/%LIBINTL_ZIP%/download %LIBINTL_ZIP%
SET LIBICONV_ZIP=libiconv-1.8-1-bin.zip
call :ensure_file https://sourceforge.net/projects/gnuwin32/files/libiconv/1.8-1/%LIBICONV_ZIP%/download %LIBICONV_ZIP%

@rem HACK: for now download libraries this way
SET JQUERY=jquery-1.11.3.js
call :ensure_file https://code.jquery.com/%JQUERY% %JQUERY%
copy /y %DOWNLOAD_DIR%\%JQUERY% %LOCAL_DIR%\..\WeatherSHIELD\gui\js\%JQUERY%
SET JQUERY_MIN=jquery-1.11.3.min.js
call :ensure_file https://code.jquery.com/%JQUERY_MIN% %JQUERY_MIN%
copy /y %DOWNLOAD_DIR%\%JQUERY_MIN% %LOCAL_DIR%\..\WeatherSHIELD\gui\js\%JQUERY_MIN%
SET JQUERY_VALIDATE_ZIP=1.11.1.zip
call :ensure_file https://github.com/jquery-validation/jquery-validation/archive/%JQUERY_VALIDATE_ZIP% %JQUERY_VALIDATE_ZIP%
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%JQUERY_VALIDATE_ZIP% %DOWNLOAD_DIR%
copy /y %DOWNLOAD_DIR%\jquery-validation-1.11.1\jquery.validate.js %LOCAL_DIR%\..\WeatherSHIELD\gui\js\
SET JSPDF_ZIP=v1.2.61.zip
call :ensure_file https://github.com/MrRio/jsPDF/archive/%JSPDF_ZIP% %JSPDF_ZIP%
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%JSPDF_ZIP% %DOWNLOAD_DIR%
IF NOT EXIST "%LOCAL_DIR%\..\WeatherSHIELD\gui\js\jspdf" mkdir "%LOCAL_DIR%\..\WeatherSHIELD\gui\js\jspdf"
copy /y %DOWNLOAD_DIR%\jsPDF-1.2.61\dist\jspdf.min.js %LOCAL_DIR%\..\WeatherSHIELD\gui\js\jspdf\jspdf.js
SET CHARTJS_ZIP=v2.9.3.zip
call :ensure_file https://github.com/chartjs/Chart.js/archive/%CHARTJS_ZIP% %CHARTJS_ZIP%
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%CHARTJS_ZIP% %DOWNLOAD_DIR%
@rem FIX: downloading but not actually using this because right now the code is overridden and can't figure out how to put that in external file

@rem need to install .NET 3.5 so do that first so it doesn't prompt user
DISM /Online /Enable-Feature /FeatureName:NetFx3 /All

set USERS=%USERS% %EXTRA_USERS%
echo Install SQL Server with admin accounts for: %USERS%
@rem setting this for windows 7 for some reason
SET SQLSVCACCOUNT=/SQLSVCACCOUNT="NT AUTHORITY\SYSTEM"
IF DEFINED ISWIN10 (
    @rem just use default
    SET SQLSVCACCOUNT=
    @rem this is default in gui
    @rem SET SQLSVCACCOUNT=/SQLSVCACCOUNT="NT AUTHORITY\NETWORK SERVICE"
)
%DOWNLOAD_DIR%\%SQLINSTALL% /QS /IAcceptSQLServerLicenseTerms /ACTION=install /INSTANCENAME=SQLEXPRESS %SQLSVCACCOUNT% /FEATURES=SSMS,SQLEngine,Replication,SDK /SQMREPORTING=0 /SAPWD=4h5n4dm1np455w0rd! /SQLSYSADMINACCOUNTS=%USERS% /SECURITYMODE=SQL /ERRORREPORTING=0

@rem need to add %SQLBINPATH% to path for sqlcmd to work
set PATH=%PATH%;%SQLBINPATH%
@rem Note that the single " being used is intentional
@rem IF NOT DEFINED ISWIN10 (
    @rem seems to include path automatically
setx /M PATH "%PATH%
@rem )

echo Setting up ODBC connection
@rem why is this 11.0 on some machines?
odbcconf.exe /a {CONFIGSYSDSN "SQL Server Native Client 10.0" "DSN=WX|Description=WX|SERVER=.\SQLEXPRESS|Database=WX"}
odbcconf.exe /a {CONFIGSYSDSN "SQL Server Native Client 10.0" "DSN=HINDCAST|Description=HINDCAST|SERVER=.\SQLEXPRESS|Database=HINDCAST"}
IF DEFINED ProgramFiles(x86) (
    pushd %SYSTEMROOT%\SysWOW64
    odbcconf.exe /a {CONFIGSYSDSN "SQL Server Native Client 10.0" "DSN=WX|Description=WX|SERVER=.\SQLEXPRESS|Database=WX"}
    odbcconf.exe /a {CONFIGSYSDSN "SQL Server Native Client 10.0" "DSN=HINDCAST|Description=HINDCAST|SERVER=.\SQLEXPRESS|Database=HINDCAST"}
    popd
)


echo Checking for python
echo %PATH% | findstr /R /C:"C:\\Python27\\ArcGIS10\..;C:\\Python27\\ArcGIS10\..\\Scripts;">nul && goto :havePath

echo Installing python
@rem default to ArcGIS10.3
SET PYTHONHOME=C:\Python27\ArcGIS10.3
msiexec /I %DOWNLOAD_DIR%\python-2.7.18.msi /qb TARGETDIR=%PYTHONHOME% ALLUSERS=1 ADDLOCAL=ALL

@rem add to path
echo %PATH% | findstr /C:%PYTHONHOME%;%PYTHONHOME%\Scripts; >nul || goto :addToPath
goto :havePath

:addToPath
set PATH=%PYTHONHOME%;%PYTHONHOME%\Scripts;%PATH%
@rem Note that the single " being used is intentional
setx /M PATH "%PATH%

:havePath
echo Have path:
echo %PATH%

pushd lib
@rem need to call from python so we can overwrite pip.exe
python -m pip install --upgrade pip-20.2.3-py2.py3-none-any.whl setuptools-20.10.1-py2.py3-none-any.whl
pip install wheel-0.35.1-py2.py3-none-any.whl
pip install pyodbc-4.0.30-cp27-cp27m-win32.whl
pip install python_dateutil-2.8.1-py2.py3-none-any.whl
pip install six-1.15.0-py2.py3-none-any.whl
pip install pytz-2020.1-py2.py3-none-any.whl
pip install numpy-1.11.0+mkl-cp27-cp27m-win32.whl --ignore-installed
easy_install numexpr-2.4.win32-py2.7.exe
pip install pandas-0.17.1-cp27-none-win32.whl
pip install netCDF4-1.2.3.1-cp27-cp27m-win32.whl
pip install --upgrade urllib3-1.22-py2.py3-none-any.whl
pip install pycparser-2.20-py2.py3-none-any.whl
pip install cffi-1.14.2-cp27-cp27m-win32.whl
pip install ipaddress-1.0.23-py2.py3-none-any.whl
pip install enum34-1.1.10-py2-none-any.whl
pip install cryptography-3.1-cp27-cp27m-win32.whl
pip install pyOpenSSL-18.0.0-py2.py3-none-any.whl
pip install certifi-2018.1.18-py2.py3-none-any.whl

@rem firestarr section
@rem relies on weathershield being installed previously
easy_install Shapely-1.4.4.win32-py2.7.exe
easy_install GDAL-1.11.1.win32-py2.7.exe
pip install click-3.1-py2.py3-none-any.whl
easy_install Fiona-1.4.8.win32-py2.7.exe
pip install Cython-0.21.2-cp27-none-win32.whl
easy_install pyproj-1.9.4dev.win32-py2.7.exe
pip install pyparsing-2.4.6-py2.py3-none-any.whl --ignore-installed
easy_install matplotlib-1.4.2.win32-py2.7.exe
pip install descartes-1.0-py2-none-any.whl
pip install geopandas-0.1.1-py2-none-any.whl
pip install functools32-3.2.3.post2-py2-none-any.whl
pip install urllib3-1.22-py2.py3-none-any.whl
pip install selenium-3.141.0-py2.py3-none-any.whl
pip install PyPDF2-1.26.0-py2-none-any.whl
pip install fpdf-1.7.2-py2.py3-none-any.whl
popd

@rem MAKE SURE ORACLE IS INSTALLED BEFORE PROCEEDING IF REQUIRED


:installIIS
%DOWNLOAD_DIR%\dotNetFx40_Full_x86_x64.exe /passive /norestart

@rem this all seems to work
set OTHER=
IF DEFINED ISWIN10 (
    set OTHER=/FeatureName:IIS-ASPNET45 /FeatureName:NetFx4Extended-ASPNET45 /FeatureName:IIS-NetFxExtensibility45
)
DISM /Online /Enable-Feature %OTHER% /FeatureName:IIS-ApplicationDevelopment /FeatureName:IIS-ASP /FeatureName:IIS-ASPNET /FeatureName:IIS-CGI /FeatureName:IIS-CommonHttpFeatures /FeatureName:IIS-DefaultDocument /FeatureName:IIS-DirectoryBrowsing /FeatureName:IIS-HealthAndDiagnostics /FeatureName:IIS-HostableWebCore /FeatureName:IIS-HttpCompressionStatic /FeatureName:IIS-HttpErrors /FeatureName:IIS-HttpLogging /FeatureName:IIS-IIS6ManagementCompatibility /FeatureName:IIS-ISAPIExtensions /FeatureName:IIS-ISAPIFilter /FeatureName:IIS-LegacyScripts /FeatureName:IIS-LegacySnapIn /FeatureName:IIS-ManagementConsole /FeatureName:IIS-ManagementScriptingTools /FeatureName:IIS-ManagementService /FeatureName:IIS-Metabase /FeatureName:IIS-NetFxExtensibility /FeatureName:IIS-Performance /FeatureName:IIS-RequestFiltering /FeatureName:IIS-RequestMonitor /FeatureName:IIS-Security /FeatureName:IIS-ServerSideIncludes /FeatureName:IIS-StaticContent /FeatureName:IIS-WebServer /FeatureName:IIS-WebServerManagementTools /FeatureName:IIS-WebServerRole /FeatureName:IIS-WMICompatibility /FeatureName:WAS-ConfigurationAPI /FeatureName:WAS-NetFxEnvironment /FeatureName:WAS-ProcessModel /FeatureName:WAS-WindowsActivationService
@rem add IIS Authentication to windows 10 home


@echo off
setlocal
for /f "delims=" %%f in ('dir /b %%SystemRoot%%\servicing\Packages\Microsoft-Windows-IIS-WebServer-AddOn-2-Package~31bf3856ad364e35~amd64~~10.0.*.1.mum') do (
  echo Installing %%f
  @echo on
  DISM /Online /norestart /add-package:"%SystemRoot%\servicing\Packages\%%f"
  @echo off
  echo.
)
endlocal
DISM /Online /Enable-Feature /FeatureName:IIS-WindowsAuthentication

mkdir %PHPDIR%
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%PHP% %PHPDIR%


%DOWNLOAD_DIR%\SQLSRV58.EXE /Q /T:%PHPDIR%\ext

copy %PHPDIR%\php.ini-production %PHPDIR%\php.ini /y
echo extension = php_sqlsrv_74_nts_x64.dll >> %PHPDIR%\php.ini
echo extension = php_pdo_sqlsrv_74_nts_x64.dll >> %PHPDIR%\php.ini


SET APPCMD=%windir%\system32\inetsrv\appcmd.exe
REM Clear current PHP handlers
%APPCMD% clear config /section:system.webServer/fastCGI
%APPCMD% set config /section:system.webServer/handlers /-[name='PHP_via_FastCGI']

REM Set up the PHP handler
%APPCMD% set config /section:system.webServer/fastCGI /+[fullPath='%phpdir%\php-cgi.exe']
%APPCMD% set config /section:system.webServer/handlers /+[name='PHP_via_FastCGI',path='*.php',verb='*',modules='FastCgiModule',scriptProcessor='%phpdir%\php-cgi.exe',resourceType='Unspecified']
%APPCMD% set config /section:system.webServer/handlers /accessPolicy:Read,Script

REM Configure FastCGI Variables
%APPCMD% set config -section:system.webServer/fastCgi /[fullPath='%phpdir%\php-cgi.exe'].instanceMaxRequests:10000
%APPCMD% set config -section:system.webServer/fastCgi /+"[fullPath='%phpdir%\php-cgi.exe'].environmentVariables.[name='PHP_FCGI_MAX_REQUESTS',value='10000']"
%APPCMD% set config -section:system.webServer/fastCgi /+"[fullPath='%phpdir%\php-cgi.exe'].environmentVariables.[name='PHPRC',value='%phpdir%\php.ini']"

REM set default document
%APPCMD% set config /section:defaultDocument /enabled:true
%APPCMD% set config /section:defaultDocument /+files.[value='index.php']

net stop "World Wide Web Publishing Service"
net start "World Wide Web Publishing Service"





msiexec /i %DOWNLOAD_DIR%\msodbcsql.msi /qb IACCEPTMSODBCSQLLICENSETERMS=YES

pushd %WINDIR%\system32\inetsrv
appcmd add apppool /name:wxshield  /managedRuntimeVersion:v4.0 /managedPipelineMode:Integrated
popd

@rem link this way so git works still
mklink /J C:\inetpub\wwwroot\wxshield C:\FireGUARD\WeatherSHIELD\gui 

pushd %WINDIR%\system32\inetsrv
appcmd add app /site.name:"Default Web Site"  /path:/wxshield /physicalPath:C:\inetpub\wwwroot\wxshield /applicationPool:wxshield

IF NOT DEFINED ISWIN10 (
    c:\Windows\Microsoft.NET\Framework\v4.0.30319\aspnet_regiis.exe -i
)
popd

@rem set permissions for web folder so IIS_IUSRS can work
icacls C:\FireGUARD\WeatherSHIELD\gui\* /T /grant IIS_IUSRS:(RX)
icacls %PHPDIR%\* /T /grant IIS_IUSRS:(RX)

echo Setting up doxygen
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%DOXYGEN_ZIP% %LOCAL_DIR%\..\documentation\doxygen

echo Setting up dia
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%DIA_ZIP% %LOCAL_DIR%\..\documentation\dia

echo Setting up graphviz
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%GV_ZIP% %LOCAL_DIR%\..\documentation

echo Generating documentation
call %LOCAL_DIR%\..\documentation\make.bat

echo Hosting documentation in IIS
pushd %LOCAL_DIR%\..\documentation\html
mklink /d C:\inetpub\wwwroot\FireGUARD %CD%
popd


echo Getting pdfsizeopt
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%PDFSIZEOPT_ZIP% %LOCAL_DIR%\..\FireSTARR\pdfsizeopt

echo Getting chromedriver
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%CHROME_ZIP% %LOCAL_DIR%\..\FireSTARR

echo Getting wgrib2
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%WGRIB_ZIP% %LOCAL_DIR%\..\WeatherSHIELD
@rem need cygwin1.dll
@rem need something to extract .xz
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%_7Z_ZIP% %DOWNLOAD_DIR%

@rem just download directly since we only need the one dll
@rem FIX: change to use some kind of library instead of wgrib2 so this isn't required
pushd %DOWNLOAD_DIR%
7za x -y %CYGWIN_XZ%
7za x -y %CYGWIN_TAR%
copy /y usr\bin\cygwin1.dll %LOCAL_DIR%\..\WeatherSHIELD\wgrib2-v0.1.9.4\bin
popd

echo Getting sed
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%SED_ZIP% %LOCAL_DIR%\..\WeatherSHIELD\db\sed
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%LIBINTL_ZIP% %LOCAL_DIR%\..\WeatherSHIELD\db\sed
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%LIBICONV_ZIP% %LOCAL_DIR%\..\WeatherSHIELD\db\sed


@rem need to add this manually for now since we didn't reopen prompt after install sql server
SET PATH=%SQLBINPATH%;%PATH%
pushd ..\WeatherSHIELD\db
call init.bat
popd

echo Adding scheduled tasks for WeatherSHIELD data collection
SCHTASKS /CREATE /SC DAILY /TN "WxSHIELD NAEFS" /TR "%SystemRoot%\system32\wscript.exe //nologo c:\FireGUARD\util\runinvisible.vbs C:\FireGUARD\WeatherSHIELD\run.bat" /ST 00:01 /RI 30 /du 24:00
SCHTASKS /CREATE /SC DAILY /TN "WxSHIELD FPA" /TR "%SystemRoot%\system32\wscript.exe //nologo c:\FireGUARD\util\runinvisible.vbs C:\FireGUARD\WeatherSHIELD\runfpa.bat" /ST 00:03 /RI 5 /du 24:00
SCHTASKS /CREATE /SC DAILY /TN "FireSTARR" /TR "%SystemRoot%\system32\wscript.exe //nologo C:\FireGUARD\util\runinvisible.vbs C:\FireGUARD\FireSTARR\firescurrent.bat" /ST 00:05 /RI 5 /du 24:00

SCHTASKS /RUN /TN "WxSHIELD NAEFS"
SCHTASKS /RUN /TN "WxSHIELD FPA"
SCHTASKS /RUN /TN "FireSTARR"

goto :end

:ensure_file
@rem need to set proper security protocol
@rem use DownloadFile instead of WebRequest due to speed difference
@rem PowerShell [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]'Tls,Tls11,Tls12';  (new-object System.Net.WebClient).DownloadFile('%1', '%2')
@echo off
pushd %DOWNLOAD_DIR%
IF NOT EXIST "%2" (
    echo Downloading %2
    @rem use -UserAgent 'Wget/1.13.4 (linux-gnu)' so that sourceforge download works
    PowerShell [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]'Tls,Tls11,Tls12';  $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%1' -OutFile '%2' -UserAgent 'Wget/1.13.4 ^(linux-gnu^)'
)
IF NOT EXIST "%2" (
    exit 1
)
popd
@echo on
goto :end


:end
