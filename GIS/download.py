import os

URL_ROOT = 'https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb'

LOCAL_DIR = r'C:\FireGUARD\GIS'
DOWNLOAD_DIR = os.path.join(LOCAL_DIR, 'download')
os.mkdir(DOWNLOAD_DIR)

set WGET=wget --no-check-certificate -c

mkdir %DOWNLOAD_DIR%
pushd %DOWNLOAD_DIR%
call :get OHNWBDY.zip
call :get WETLAND.zip
call :get INDIANRE.zip
call :get PROVPREG.zip
call :get CONRVREG.zip
call :get OHNWCRS.zip
call :get MNRRDSEG.zip
call :get ORNSEGAD.zip
call :get UTILLINE.zip
call :get ORWNTRK.zip
call :get UTILSITE.zip
call :get FISHAPNT.zip
call :get BUILDSYM.zip
call :get AIRPTOFF.zip
call :get MNRDIST.zip

@rem Listed on GEOHUB but not available for download
@rem TOURISM_ESTABLISHMENT_AREA
@rem COTTAGE_RESIDENTIAL_SITE
@rem FIRE_COMMUNICATIONS_TOWER
@rem RECREATION_POINT
@rem CL_NON_FREEHOLD_DISPOSITION
@rem FIRE_RESPONSE_SECTOR


@rem ***NOT ON GEOHUB***
@rem BOAT_CACHE_LOCATION
@rem TRAPPER_CABIN


@rem Provincial features that aren't on GEOHUB:
@rem COMMUNITIES
@rem CITIESMAJOR
@rem PROVINCIAL_FIRE_BLOCKS
@rem PROVINCIAL_FIRE_INDEX
popd

popd
goto :end

:get
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/%1
Powershell Expand-Archive -Force %DOWNLOAD_DIR%\%1



:end
