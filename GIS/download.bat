set WGET=wget --no-check-certificate -c
mkdir download
pushd download
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/OHNWBDY.zip
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/WETLAND.zip
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/INDIANRE.zip
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/PROVPREG.zip
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/CONRVREG.zip
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/OHNWCRS.zip
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/MNRRDSEG.zip
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/ORNSEGAD.zip
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/UTILLINE.zip
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/ORWNTRK.zip
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/UTILSITE.zip
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/FISHAPNT.zip
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/BUILDSYM.zip
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/AIRPTOFF.zip
%WGET% https://www.gisapplication.lrc.gov.on.ca/fmedatadownload/Packages/fgdb/MNRDIST.zip

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
