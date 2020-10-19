"""Gets ocean temperature indices and collates them"""

import sys
sys.path.append('..\util')
import common
import csv
import netCDF4
import pandas as pd
import datetime
import os
import numpy
import pyodbc
import math
import logging

## directory to use for data save/load
DIR_DATA = 'data/sst'

## Nino 1+2
url_nino1_2 = r'http://www.cpc.ncep.noaa.gov/products/people/wwang/cfsv2fcst/dataInd3/nino12Mon.nc'
## Nino 3
url_nino3 = r'http://www.cpc.ncep.noaa.gov/products/people/wwang/cfsv2fcst/dataInd3/nino3Mon.nc'
## Nino 3.4
url_nino3_4 = r'https://www.cpc.ncep.noaa.gov/products/people/wwang/cfsv2fcst/dataInd3/nino34Mon.nc'
## Nino 4
url_nino4 = r'http://www.cpc.ncep.noaa.gov/products/people/wwang/cfsv2fcst/dataInd3/nino4Mon.nc'

def save_file(url):
    """!
    Save the given url
    @param url URL to save
    @return path to saved file from URL
    """
    return common.save_http(DIR_DATA, url)

def getValues(name, url):
    """!
    Get values for given name and url
    @param name Name of values to load
    @param url URL to load from
    @return pandas DataFrame with loaded data
    """
    input = netCDF4.Dataset(save_file(url))
    times = input.variables['TIME']
    jd = netCDF4.num2date(times[:], times.units)
    num = len(input.variables['ENS'])
    values = []
    for t in xrange(len(jd)):
        sum = 0
        count = 0
        for x in xrange(num):
            val = input.variables['anom'][x][t][0][0][0]
            #~ print val
            if '--' != val:
                #~ print x
                sum += float(val)
                count += 1
        #~ print jd[t], sum / count
        values.append(sum / count)
    df = pd.DataFrame(zip(jd, values))
    df.columns = ["Date", name]
    return df

def load():
    """!
    Load data for all indices
    @return pandas DataFrame of loaded data
    """
    if common.CURRENT_PROXY is not None and common.CURRENT_PROXY.endswith(common.MNR_PROXY):
        common.set_proxy(None)
    common.check_proxy()
    nino1_2 = getValues("Nino1+2", url_nino1_2)
    nino3 = getValues("Nino3", url_nino3)
    nino3_4 = getValues("Nino3.4", url_nino3_4)
    nino4 = getValues("Nino4", url_nino4)
    all = pd.merge(pd.merge(pd.merge(nino1_2, nino3), nino3_4), nino4).set_index(['Date']).transpose()
    all.index.name = 'Index'
    all.to_csv(r'C:\inetpub\wwwroot\wxshield\nino.csv')
    return all
