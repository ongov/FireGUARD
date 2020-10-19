"""Load reanalysis data"""
import sys
sys.path.append('..\util')
import common
import csv
import netCDF4
import pandas
import datetime
import os
import numpy
import pyodbc
import math
import logging


## Provides mapping between fields we're looking for and the file names that contain them
file_masks = {
    r'TMIN': r'Datasets/ncep.reanalysis/surface_gauss/tmin.2m.gauss.{}.nc',
    r'TMAX': r'Datasets/ncep.reanalysis/surface_gauss/tmax.2m.gauss.{}.nc',
    r'TMP': r'Datasets/ncep.reanalysis/surface_gauss/air.2m.gauss.{}.nc',
    r'UGRD' : r'Datasets/ncep.reanalysis/surface_gauss/uwnd.10m.gauss.{}.nc',
    r'VGRD': r'Datasets/ncep.reanalysis/surface_gauss/vwnd.10m.gauss.{}.nc',
    r'SHUM': r'Datasets/ncep.reanalysis/surface_gauss/shum.2m.gauss.{}.nc',
    r'PRATE': r'Datasets/ncep.reanalysis/surface_gauss/prate.sfc.gauss.{}.nc'
}

## Name to use for model data
MODEL_NAME = 'Reanalysis1v05'

## directory to use for data save/load
DIR_DATA = 'data/reanalysis1'
common.ensure_dir(DIR_DATA)

def save_file(filename):
    """!
    Save the given url
    @param filename URL to save
    @return Path that file was saved to
    """
    print filename
    return common.save_ftp(DIR_DATA,
                               '/'.join([common.CONFIG.get('FireGUARD', 'reanalysis_server'), filename]),
                               user=common.CONFIG.get('FireGUARD', 'reanalysis_server_user'),
                               password=common.CONFIG.get('FireGUARD', 'reanalysis_server_password'),
                               ignore_existing=True)


def get_valid_locs(lats, lons):
    """!
    Determine which indexes in the 2d array provide lat/long coordinates within our bounds
    @param lats Dictionary of latitude min and max
    @param lons Dictionary of longitude min and max
    @return 2d array of all valid combinations of lat/long within the bounds
    """
    lon_min = (float(common.BOUNDS['longitude']['min']) + 360) % 360
    lon_max = (float(common.BOUNDS['longitude']['max']) + 360) % 360
    lat_min = float(common.BOUNDS['latitude']['min'])
    lat_max = float(common.BOUNDS['latitude']['max'])
    lat_inds = numpy.where((lats[:] > lat_min) & (lats[:] < lat_max))
    lon_inds = numpy.where((lons[:] > lon_min) & (lons[:] < lon_max))
    import itertools
    valid = list(itertools.product(lat_inds[0], lon_inds[0]))
    return valid


def get_Dataset(year, colname):
    """!
    Open netCDF4 for desired data
    @param year Year to download data for
    @param colname Name of field to read data for
    @return netCDF4.Dataset of data read
    """
    print year, colname
    file = file_masks[colname].format(year)
    filename = None
    if 1981 == year and 'TMP' == colname:
        logging.debug("Using workaround for 1981 temperature download issue")
        # HACK to use file from alternate source since other won't download
        other_url = r'http://database.rish.kyoto-u.ac.jp/arch/ncep/data/ncep.reanalysis/surface_gauss/air.2m.gauss.1981.nc'
        def save_other(url):
            return common.save_http(DIR_DATA, url)
        filename = common.try_save(save_other, other_url)
    else:
        filename = common.try_save(save_file, file)
    #~ filename = os.path.join(DIR_DATA, os.path.basename(file))
    return netCDF4.Dataset(filename)


# http://earthscience.stackexchange.com/questions/2360/how-do-i-convert-specific-humidity-to-relative-humidity
def rh_from_sh(shum, tmp, pressure = 1013.25):
    """!
    Convert specific humidity to relative humidity
    @param shum Specific humidity (dimensionless, e.g. kg/kg)
    @param tmp Temperature (Celcius)
    @param pressure Pressure (mb)
    @return Relative Humidity (%)
    """
    es = 6.112 * math.exp((17.67 * tmp) / (tmp + 243.5))
    e = shum * pressure / (0.378 * shum + 0.622)
    rh = e / es
    return rh * 100


def get_year(year):
    """!
    Load data for given year
    @param year Year to load data for
    @return pandas.DataFrame with data for all indices for the year
    """
    tmin = get_Dataset(year, 'TMIN')
    tmax = get_Dataset(year, 'TMAX')
    tmp = get_Dataset(year, 'TMP')
    ugrd = get_Dataset(year, 'UGRD')
    vgrd = get_Dataset(year, 'VGRD')
    shum = get_Dataset(year, 'SHUM')
    prate = get_Dataset(year, 'PRATE')
    lats = tmp.variables['lat']
    lons = tmp.variables['lon']
    times = tmp.variables['time']
    jd = netCDF4.num2date(times[:], times.units)
    valid = get_valid_locs(lats, lons)
    # every day is the first key?
    index = ['Model', 'Year', 'ForTime', 'Latitude', 'Longitude']
    stations = []
    # HACK: determine length of each period in the data
    period = datetime.datetime.strptime(prate.variables['time'].delta_t, '0000-00-00 %H:%M:%S')
    t_d = (period - datetime.datetime(1900, 1, 1)).seconds
    # determine number of periods that make up 1 day
    t_p = 86400 / t_d
    # determine number of whole periods between 0800 and 1300
    t_0800_start = 18000 / t_d
    # determine how much of last partial period is between 1300 and 0800
    t_0800_rem = (1.0 - (18000.0 % t_d) / t_d)
    for t in xrange(len(jd)):
        # t = 6
        #~ if 4 <= jd[t].day:
            #~ break
        if 18 == jd[t].hour:
            print jd[t]
            v_tmin = tmin.variables['tmin'][t]
            v_tmax = tmax.variables['tmax'][t]
            v_tmp = tmp.variables['air'][t]
            v_ugrd = ugrd.variables['uwnd'][t]
            v_vgrd = vgrd.variables['vwnd'][t]
            v_shum = shum.variables['shum'][t]
            def calc_values(x):
                # HACK: just ignore precip for Dec 31, 18z - 24z
                # convert from rate to amount
                apcp_24 = sum(prate.variables['prate'][max(0, t-t_p):t,x[0],x[1]]) * t_d
                # determine how much rain happened between 1300 - 0800 and 0800 - 1300
                # get rain from whole periods before 0800
                apcp_0800_whole = sum(prate.variables['prate'][max(0, t-t_p):(t-(t_0800_start+1)),x[0],x[1]]) * t_d
                # get rain from last partial period
                apcp_0800_partial = sum(prate.variables['prate'][(t-(t_0800_start+1)):(t-t_0800_start),x[0],x[1]]) * t_d
                # determine how much rain happened up to 0800
                apcp_0800 = apcp_0800_whole + apcp_0800_partial * t_0800_rem
                c_apcp = max(0, apcp_24 - 1.25)
                apcp_ratio = 1.0 if 0.0 == apcp_24 else apcp_0800 / apcp_24
                c_t1800 = common.kelvin_to_celcius(v_tmp[x])
                c_tmin = common.kelvin_to_celcius(min(tmin.variables['tmin'][(t-2):(t+2),x[0],x[1]]))
                c_tmax = common.kelvin_to_celcius(max(tmax.variables['tmax'][(t-2):(t+2),x[0],x[1]]))
                def calc_e(temp):
                    return 6.1078*math.pow(10, (7.5*temp)/(237.3+temp))
                e_tmin = calc_e(c_tmin)
                e_t1800 = calc_e(c_t1800)
                RH_tmin = (e_tmin / e_t1800) * 100
                sq = v_shum[x]
                if apcp_24 > 1.0:
                    if sq > 0.005:
                        sq = sq - 0.0034
                elif apcp_24 > 0.1: # and apcp_24 <= 1.0
                    if sq > 0.002:
                        sq = sq - 0.001
                else: # apcp_24  <= 0.1
                    if sq > 0.002:
                        sq = sq - 0.0004
                e_sq = sq * 1013.25 / (0.378 * sq + 0.622)
                RH_sq = (e_sq / e_t1800) * 100
                if apcp_24 > 1.0:
                    c_rh = RH_tmin
                else:
                    c_rh = min(RH_tmin, RH_sq)
                # HACK: need to ensure that 0 <= RH <= 100
                c_rh = min(100, max(0, c_rh))
                return [
                            lats[x[0]],
                            lons[x[1]] if lons[x[1]] <= 180 else (lons[x[1]] - 360),
                            c_t1800,
                            c_rh,
                            common.calc_ws(v_ugrd[x], v_vgrd[x]),
                            common.calc_wd(v_ugrd[x], v_vgrd[x]),
                            c_apcp,
                            c_apcp * apcp_ratio
                        ]
            df = pandas.DataFrame(
                    map(calc_values, valid),
                    columns=['Latitude', 'Longitude', 'TMP', 'RH', 'WS', 'WD', 'APCP', 'APCP_0800'])
            df['Model'] = MODEL_NAME
            # use time from 18z
            df['ForTime'] = jd[t]
            df['Year'] = jd[t].year
            df = df.set_index(index)
            stations.append(df)
    all = pandas.concat(stations)
    # all['lon'] = all['lon'].apply(lambda x: x if x <= 180 else x - 360)
    all = all.reset_index().set_index(index).sort()
    return all

if __name__ == '__main__':
    common.check_proxy()
    # get data for each year and save it
    #~ for year in [2019]:
    cnxn = None
    try:
        cnxn = common.open_local_db('HINDCAST')
        hindcasts = pandas.read_sql('SELECT * FROM [HINDCAST].[DAT_Model] WHERE [Model]=\'{}\''.format(MODEL_NAME), cnxn)
        for year in range(1948, datetime.datetime.now().year):
            ## data for current year
            if (1 != len(hindcasts.query('Year == {}'.format(year)))):
                df = get_year(year)
                ## @cond Doxygen_Suppress
                common.insert_weather('HINDCAST', 'DAT_Hindcast', df, 'Year', 'HINDCAST', addStartDate=False)
                ## @endcond
            else:
                print('Already have {} data for {}'.format(MODEL_NAME, year))
    finally:
        if cnxn:
            cnxn.close()
