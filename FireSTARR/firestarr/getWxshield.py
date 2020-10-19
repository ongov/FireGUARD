"""Download the 11x17 version of the WeatherSHIELD pdf for a specific fire"""

import os
from selenium import webdriver
import time
from shutil import copyfile
from util import *
import sys
import argparse

from Settings import Settings

## URL for retreving WeatherSHIELD report
URL_MASK = r"http://localhost/wxshield/display.php?y={:2.4f}&x={:2.4f}&s={}&d={}&f={}"
## Path to where the exported pdf will be saved
PATH_MASK = os.path.join(os.environ['USERPROFILE'], r'Downloads\{}_{}_wxshield.pdf')
## Time to wait for respone
SLEEP_LIMIT = 30

def getURL(lat, lon, startDate, days, fire):
    """!
    Generate url for retrieving WeatherSHIELD pdf
    @param lat Latitude of point to get report for
    @param lon Longitude of point to get report for
    @param startDate Start date for report
    @param days Number of days to request
    @param fire Name of fire to label report with
    @return URL that will provide requested report
    """
    return URL_MASK.format(lat, lon, startDate, days, fire)

def getWxSHIELDFile(startDate, fire, dirname):
    """!
    Generate file name that export is saved to
    @param startDate Start date for report
    @param fire Name of fire report is for
    @param dirname Directory that report is saved in
    @return Path that report would be saved to
    """
    path = PATH_MASK.format(fire, startDate)
    return os.path.join(dirname, os.path.basename(path))

def getWxSHIELD(lat, lon, startDate, days, fire, dirname, apcp=None, ffmc=None, dmc=None, dc=None):
    """!
    Save a WeatherSHIELD report pdf
    @param lat Latitude of point to get report for
    @param lon Longitude of point to get report for
    @param startDate Start date for report
    @param days Number of days to request
    @param fire Name of fire to label report with
    @param dirname Directory to save to
    @param apcp Accumulated Precipitation at 0800 to override with
    @param ffmc Fine Fuel Moisture Code to override with
    @param dmc Duff Moisture Code to override with
    @param dc Drought Code to override with
    @return Path to saved report
    """
    # set PATH=C:\Python27\ArcGIS10.3\Lib\site-packages\chromedriver;%PATH%
    url = getURL(lat, lon, startDate, days, fire)
    if apcp or ffmc or dmc or dc:
        url += '&override=on'
        if apcp:
            url += '&setAPCP_0800={}'.format(apcp)
        if ffmc:
            url += '&setFFMC={}'.format(ffmc)
        if dmc:
            url += '&setDMC={}'.format(dmc)
        if dc:
            url += '&setDC={}'.format(dc)
    print url
    path = PATH_MASK.format(fire, startDate)
    try:
        os.remove(path)
    except:
        pass
    from selenium import webdriver
    capabilities = {
      'browserName': 'chrome',
      'chromeOptions':  {
        'useAutomationExtension': False,
        'args': [
            'window-size=1680,1050',
            'window-position=-10000,0',
            'log-level=3',
        ]
      }
    }  
    driver = webdriver.Chrome(os.path.join(Settings.HOME_DIR, 'chromedriver.exe'), desired_capabilities = capabilities)
    driver.minimize_window()
    driver.implicitly_wait(60)
    driver.get(url)
    python_button = driver.find_element_by_id('export_tabloid')
    python_button.click()
    slept = 0
    while not os.path.exists(path) and slept < SLEEP_LIMIT:
        time.sleep(1)
        slept += 1
    driver.close()
    driver.quit()
    del driver
    if not os.path.exists(path):
        # didn't work
        raise Exception("Error retrieving {}".format(url))
    to_file = getWxSHIELDFile(startDate, fire, dirname)
    print to_file
    copyfile(path, to_file)
    return to_file

def doRun():
    """!
    Run with command line arguments
    @return None
    """
    ## Command line argument parser
    parser = argparse.ArgumentParser()
    ## ! @cond Doxygen_Suppress
    parser.add_argument('lat', help='latitude')
    ## ! @endcond
    parser.add_argument('lon', help='longitude')
    parser.add_argument('startDate', help='start date for WxSHIELD run')
    parser.add_argument('days', help='duration of WxSHIELD run')
    parser.add_argument('fire', help='name of fire to label run with')
    parser.add_argument('dirname', help='directory to save output to')
    parser.add_argument("--ffmc", help="override FFMC")
    parser.add_argument("--dmc", help="override DMC")
    parser.add_argument("--dc", help="override DC")
    parser.add_argument("--apcp_0800", help="override 0800 accumulated precipitation")
    ## Parsed arguments
    args = parser.parse_args()
    ## Latitude
    lat = float(args.lat)
    ## Longitude
    lon = float(args.lon)
    ## Number of days to run for
    days = int(args.days)
    ## Start date of forecast
    startDate = args.startDate
    ## Name of fire to use on forecast
    fire =  args.fire
    ## Directory to save output to
    dirname = args.dirname
    ## Overridden Accumulated Precipitation at 0800
    apcp_0800 = args.apcp_0800
    ## Overridden Fine Fuel Moisture Code
    ffmc = args.ffmc
    ## Overridden Duff Moisture Code
    dmc = args.dmc
    ## Overridden Drought Code
    dc = args.dc
    try:
        getWxSHIELD(lat, lon, startDate, days, fire, dirname, apcp_0800, ffmc, dmc, dc)
    except:
        sys.exit(-1)

if __name__ == '__main__':
    doRun()