"""Shared code"""

import math
import urllib2
from urlparse import urlparse
import dateutil
import time
import dateutil.parser
import datetime
import os
import pyodbc
import io
import subprocess
import shlex
import pandas
import logging
import ConfigParser
import re
import numpy
import shutil
import _winreg
import certifi
import ssl

## So HTTPS transfers work properly
#~ ssl._create_default_https_context = ssl._create_unverified_context

## bounds to use for clipping data
BOUNDS = None

## file to load settings from
SETTINGS_FILE = r'..\settings.ini'
## currently set proxy
CURRENT_PROXY = None
## loaded configuration
CONFIG = None

## @cond Doxygen_Suppress
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
## @endcond

def ensure_dir(dir):
    """!
    Check if directory exists and make it if not
    @param dir Directory to ensure existence of
    @return None
    """
    if not os.path.exists(dir):
        os.makedirs(dir)


def read_config(force=False):
    """!
    Read configuration from default file
    @param force Force reading even if already loaded
    @return None
    """
    global CONFIG
    global BOUNDS
    logging.debug('Reading config file {}'.format(SETTINGS_FILE))
    if force or CONFIG is None:
        CONFIG = ConfigParser.SafeConfigParser()
        # set default values and then read to overwrite with whatever is in config
        CONFIG.add_section('FireGUARD')
        # NOTE: should use if this is required to work while proxy isn't already authenticated
        # CONFIG.set('Proxy', 'address', '<user>:<password>@ipv4:port')
        CONFIG.set('FireGUARD', 'proxy', '')
        CONFIG.set('FireGUARD', 'email', '<SUPPORT_EMAIL@DOMAIN.COM>')
        CONFIG.set('FireGUARD', 'active_offer', 'For accessibility accommodations, alternate formats, questions, or feedback, please contact')
        CONFIG.set('FireGUARD', 'fire_root', '')
        CONFIG.set('FireGUARD', 'output_default', '')
        CONFIG.set('FireGUARD', 'perim_archive_root', '')
        CONFIG.set('FireGUARD', 'perim_root', '')
        CONFIG.set('FireGUARD', 'latitude_min', '41')
        CONFIG.set('FireGUARD', 'latitude_max', '58')
        CONFIG.set('FireGUARD', 'longitude_min', '-96')
        CONFIG.set('FireGUARD', 'longitude_max', '-73')
        CONFIG.set('FireGUARD', 'dfoss_connection', '')
        CONFIG.set('FireGUARD', 'url_agency_wx', '')
        CONFIG.set('FireGUARD', 'url_agency_wx_longrange', '')
        CONFIG.set('FireGUARD', 'fpa_locations_grid', '')
        CONFIG.set('FireGUARD', 'reanalysis_server', 'ftp://ftp.cdc.noaa.gov')
        CONFIG.set('FireGUARD', 'reanalysis_server_user', '')
        CONFIG.set('FireGUARD', 'reanalysis_server_password', '')
        CONFIG.set('FireGUARD', 'naefs_server', 'https://nomads.ncep.noaa.gov/cgi-bin/')
        try:
            with open(SETTINGS_FILE) as configfile:
                CONFIG.readfp(configfile)
        except:
            logging.info('Creating new config file {}'.format(SETTINGS_FILE))
            with open(SETTINGS_FILE, 'wb') as configfile:
                CONFIG.write(configfile)
        BOUNDS = {
            'latitude': {
                'min': int(CONFIG.get('FireGUARD', 'latitude_min')),
                'max': int(CONFIG.get('FireGUARD', 'latitude_max'))
            },
            'longitude': {
                'min': int(CONFIG.get('FireGUARD', 'longitude_min')),
                'max': int(CONFIG.get('FireGUARD', 'longitude_max'))
            }
        }


# HACK: need to do this every time file is loaded or else threads might get to it first
read_config()


def set_proxy(address, verbose=True):
    """!
    Set proxy to given address
    @param address Proxy address
    @param verbose Whether or not to output proxy settings
    @return None
    """
    if verbose:
        # HACK: blank out password in logs
        safe_address = address
        if address is not None and -1 != address.find('@'):
            safe_address = re.sub('(.*):(.*)@(.*)', '\\1:<password>@\\3', address)
        logging.debug("Setting proxy to {}".format(safe_address))
    global CURRENT_PROXY
    CURRENT_PROXY = address
    proxy = urllib2.ProxyHandler(None if address is None else {'http': address, 'https': address})
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)


def check_proxy():
    """!
    Check if proxy should be used
    @return Whether or not proxy should be used
    """
    try:
        # reset to none before checking because otherwise it hangs checking if it's already set
        set_proxy(None, False)
        # if we can reach the proxy config file then use the proxy
        # HACK: for now just use registry key .pac file to check if on proxy 
        #       but still require proxy in settings
        with _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                              "SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings") as k:
            proxy = _winreg.QueryValueEx(k, 'AutoConfigURL')
            response = urllib2.urlopen(proxy)
            set_proxy(CONFIG.get('FireGUARD', 'proxy'))
        return True
    except:
        return False

def fix_timezone_offset(d):
    """!
    Convert from UTC to local time, respecting DST if required
    @param d Date to fix timezone offset for
    @return Date converted to local time
    """
    local_offset = time.timezone
    if time.daylight:
        if time.localtime().tm_isdst > 0:
            local_offset = time.altzone
    localdelta = datetime.timedelta(seconds=-local_offset)
    # convert to local time so other ftp programs would produce same result
    return (d + localdelta).replace(tzinfo=None)


def save_http(to_dir, url, save_as=None, mode='wb', ignore_existing=False):
    """!
    Save file at given URL into given directory using an HTTP connection
    @param to_dir Directory to save into
    @param url URL to download from
    @param save_as File to save as, or None to use URL file name
    @param mode Mode to write to file with
    @param ignore_existing Whether or not to download if file already exists
    @return Path that file was saved to
    """
    logging.debug("Saving {}".format(url))
    if save_as is None:
        save_as = os.path.join(to_dir, os.path.basename(url))
    if ignore_existing and os.path.exists(save_as):
        logging.debug('Ignoring existing file')
        return save_as
    ensure_dir(to_dir)
    # we want to keep modified times matching on both ends
    do_save = True
    response = urllib2.urlopen(url)
    modlocal = None
    if 'last-modified' in response.headers.keys():
        mod = response.headers['last-modified']
        modtime = dateutil.parser.parse(mod)
        modlocal = fix_timezone_offset(modtime)
        # if file exists then compare mod times
        if os.path.isfile(save_as):
            filetime = os.path.getmtime(save_as)
            filedatetime = datetime.datetime.fromtimestamp(filetime)
            do_save = modlocal != filedatetime
    # NOTE: need to check file size too? Or should it not matter because we
    #       only change the timestamp after it's fully written
    if do_save:
        logging.info("Downloading {}".format(save_as))
        try:
            with open(save_as, mode) as f:
                f.write(response.read())
        except:
            try_remove(save_as)
            raise
        if modlocal is not None:
            tt = modlocal.timetuple()
            usetime = time.mktime(tt)
            os.utime(save_as, (usetime, usetime))
    return save_as


def save_ftp(to_dir, url, user="anonymous", password="", ignore_existing=False):
    """!
    Save file at given URL into given directory using an FTP connection
    @param to_dir Directory to save into
    @param url URL to download from
    @param user User to use for authentication
    @param password Password to use for authentication
    @param ignore_existing Whether or not to download if file already exists
    @return Path that file was saved to
    """
    urlp = urlparse(url)
    folder = os.path.dirname(urlp.path)
    site = urlp.netloc
    filename = os.path.basename(urlp.path)
    logging.debug("Saving {}".format(filename))
    import ftplib
    #logging.debug([to_dir, url, site, user, password])
    ftp = ftplib.FTP(site)
    ftp.login(user, password)
    ftp.cwd(folder)
    save_as = os.path.join(to_dir, filename)
    do_save = True
    ftptime = ftp.sendcmd('MDTM {}'.format(filename))
    ftpdatetime = datetime.datetime.strptime(ftptime[4:], '%Y%m%d%H%M%S')
    ftplocal = fix_timezone_offset(ftpdatetime)
    # if file exists then compare mod times
    if os.path.isfile(save_as):
        if ignore_existing:
            logging.debug('Ignoring existing file')
            return save_as
        filetime = os.path.getmtime(save_as)
        filedatetime = datetime.datetime.fromtimestamp(filetime)
        do_save = ftplocal != filedatetime
    # NOTE: need to check file size too? Or should it not matter because we
    #       only change the timestamp after it's fully written
    if do_save:
        logging.debug("Downloading {}".format(filename))
        with open(save_as, 'wb') as f:
            ftp.retrbinary('RETR {}'.format(filename), f.write)
        tt = ftplocal.timetuple()
        usetime = time.mktime(tt)
        os.utime(save_as, (usetime, usetime))
    return save_as


def try_save(fct, url, max_save_retries=5):
    """!
    Use callback fct to try saving up to a fixed number of retries
    @param fct Function to apply to url
    @param url URL to apply function to
    @param max_save_retries Maximum number of times to try saving
    @return Result of calling fct on url
    """
    save_tries = 0
    while (True):
        try:
            return fct(url)
        except urllib2.URLError as ex:
            logging.warning(ex)
            # no point in retrying if URL doesn't exist
            if 404 == ex.code or save_tries >= max_save_retries:
                raise ex
            logging.warning("Retrying save for {}".format(url))
            save_tries += 1


def copy_file(filename, toname):
    """!
    Copy file and keep timestamp the same
    @param filename Source path to copy from
    @param toname Destination path to copy to
    @return None
    """
    shutil.copyfile(filename, toname)
    filetime = os.path.getmtime(filename)
    os.utime(toname, (filetime, filetime))


def calc_rh(Td, T):
    """!
    Calculate RH based on dewpoint temp and temp
    @param Td Dewpoint temperature (Celcius)
    @param T Temperature (Celcius)
    @return Relative Humidity (%)
    """
    m = 7.591386
    Tn = 240.7263
    return 100 * pow(10, (m * ((Td / (Td + Tn)) - (T / (T + Tn)))))


def calc_ws(u, v):
    """!
    Calculate wind speed in km/h from U and V wind given in m/s
    @param u Wind vector in U direction (m/s)
    @param v Wind vector in V direction (m/s)
    @return Calculated wind speed (km/h)
    """
    # NOTE: convert m/s to km/h
    return 3.6 * math.sqrt(u * u + v * v)


def calc_wd(u, v):
    """!
    Calculate wind direction from U and V wind given in m/s
    @param u Wind vector in U direction (m/s)
    @param v Wind vector in V direction (m/s)
    @return Wind direction (degrees)
    """
    return ((180 / math.pi * math.atan2(-u, -v)) + 360) % 360


def kelvin_to_celcius(t):
    """!
    Convert temperature in Kelvin to Celcius 
    @param t Temperature (Celcius)
    @return Temperature (Kelvin)
    """
    return t - 273.15


def make_insert_statement(table, columns, no_join=True):
    """!
    Generates INSERT statement for table using column names
    @param table Table to insert into
    @param columns Columns within table
    @param no_join Whether or not to make complex statement with join
    @return INSERT statement that was created
    """
    if no_join:
        return "INSERT INTO {table}({cols}) values ({vals})".format(
                table=table,
                cols=', '.join(columns),
                vals=', '.join(['?'] * len(columns))
            )
    return """
INSERT INTO {table}({cols})
SELECT {val_cols}
FROM (VALUES ({vals})) val ({cols})
LEFT JOIN {table} d ON
    {join_stmt}
WHERE
    {null_stmt}
    """.format(
        table=table,
        cols=', '.join(columns),
        val_cols=', '.join(map(lambda x: 'val.[' + x + ']', columns)),
        join_stmt=' AND '.join(map(lambda x: 'val.[' + x + ']=d.[' + x + ']', columns)),
        null_stmt=' AND '.join(map(lambda x: 'd.[' + x + '] IS NULL', columns)),
        vals=', '.join(['?'] * len(columns))
    )


def make_sub_insert_statement(table, columns, fkId, fkName, fkTable, fkColumns):
    """!
    Generates INSERT statement for table using column names
    @param table Table to insert into
    @param columns Columns within table
    @param fkId Foreign key ID
    @param fkName Foreign key name
    @param fkTable Foreign key table
    @param fkColumns Foreign key table columns
    @return INSERT statement that was created
    """
    # do this instead of using set() so order is kept
    actual_columns = [x for x in columns if x not in fkColumns]
    return """
        INSERT INTO {table}({actual_cols})
        SELECT d.{fkId} AS {fkName}, {val_cols}
        FROM
            (VALUES ({vals})) val ({cols})
            LEFT JOIN {fkTable} d
            ON {join_stmt}
        """.format(
                table=table,
                actual_cols=', '.join([fkName] + actual_columns),
                cols=', '.join(columns),
                vals=', '.join(['?'] * len(columns)),
                fkId=fkId,
                fkName=fkName,
                val_cols=', '.join(map(lambda x: 'val.[' + x + ']', actual_columns)),
                fkTable=fkTable,
                join_stmt=' AND '.join(map(lambda x: 'val.[' + x + ']=d.[' + x + ']', fkColumns))
            )


def fix_None(x):
    """!
    Convert to None instead of alternative formats that mean the same
    @param x Value to convert from
    @return None or the original value
    """
    # for some reason comparing to pandas.NaT doesn't work
    return None if isinstance(x, type(pandas.NaT)) else None if 'nan' == str(x) else x


def fix_Types(x):
    """!
    Convert to datetime if it's a numpy.datetime64, or None if it's a value for nothing
    @param x Value to convert from
    @return None, a datetime, or the original value
    """
    # for some reason the dates are giving too much precision for the database to use if seconds are specified
    if isinstance(x, numpy.datetime64):
        x = pandas.to_datetime(x)
    return fix_None(x)


def fix_execute(cursor, stmt, data):
    """!
    @param cursor Cursor to execute statement with
    @param stmt Statement to execute
    @param data Data to populate statement with
    @return None
    """
    cursor.executemany(stmt, (tuple(map(fix_Types, x)) for x in data))

def get_database(for_run):
    """!
    Return database corresponding to this date
    @param for_run Date to find database for
    @return Name of database that statement corresponds to
    """
    return 'WX_{}'.format(for_run.strftime('%Y%m'))

def open_local_db(dbname=None):
    """!
    @param dbname Name of database to open, or None to open default
    @return pyodbc connection to database
    """
    if not dbname:
        dbname = get_database(datetime.datetime.now())
    logging.debug("Opening local database connection to {}".format(dbname))
    return pyodbc.connect('DSN=WX;DATABASE={};UID=wx_readwrite;PWD=wx_r34dwr1t3p455w0rd!'.format(dbname))


def save_data(table, wx, delete_all=False, dbname=None):
    """!
    Save into database
    @param table Table to save data into
    @param wx Data to save into table
    @param delete_all Whether or not to delete data from table before saving
    @param dbname Name of database to save to
    @return None
    """
    # open connection
    cnxn = None
    try:
        cnxn = open_local_db(dbname)
        trans_save_data(cnxn, table, wx, delete_all)
        cnxn.commit()
    finally:
        if cnxn:
            cnxn.close()


def trans_delete_data(cnxn, table, wx, delete_all=False):
    """!
    Delete data give from table so that it can be replaced
    @param cnxn Connection to use for query
    @param table Table to insert data into
    @param wx Data to insert into table
    @param delete_all Whether or not to delete all data from table before inserting
    @return None
    """
    cursor = cnxn.cursor()
    # Assumption is that every save we have all points for the included members
    # - still should allow us to save one member at a time though
    if delete_all:
        stmt_delete = "DELETE FROM {}".format(table)
        logging.debug("Deleting existing data using {}".format(stmt_delete))
        cursor.execute(stmt_delete)
    else:
        # DELETE statement that uses all unique values for index columns except coordinates
        non_point_indices = [x for x in wx.index.names if x not in ['Latitude', 'Longitude']]
        unique = wx.reset_index()[non_point_indices].drop_duplicates()
        stmt_delete = "DELETE FROM {} WHERE {}".format(table,
                                                       ' and '.join(map(lambda x: x + '=?', non_point_indices))
                                                       )
        logging.debug("Deleting existing data using {}".format(stmt_delete))
        logging.debug(unique.values)
        if 0 == len(unique.values):
            logging.debug("No data provided - nothing to delete or insert")
            return
        fix_execute(cursor, stmt_delete.format(table), unique.values)


def trans_save_data(cnxn, table, wx, delete_all=False):
    """!
    Save into database with given connection and don't commit
    @param cnxn Connection to use for query
    @param table Table to insert data into
    @param wx Data to insert into table
    @param delete_all Whether or not to delete all data from table before inserting
    @return None
    """
    logging.debug("Saving data to {}".format(table))
    trans_delete_data(cnxn, table, wx, delete_all)
    all_wx = wx.reset_index()
    columns = all_wx.columns
    stmt_insert = make_insert_statement(table, columns)
    trans_insert_data(cnxn, wx, stmt_insert)


def trans_insert_data(cnxn, wx, stmt_insert):
    """!
    Insert data using statement
    @param cnxn Connection to use for query
    @param wx Data to insert into table
    @param stmt_insert INSERT statement to use
    @return None
    """
    cursor = cnxn.cursor()
    index = wx.index.names
    all_wx = wx.reset_index()
    # HACK: this is returning int64 when we know they aren't
    for i in index:
        if 'int64' == all_wx[i].dtype:
            all_wx[i] = all_wx[i].astype(int)
    logging.debug("Inserting {} rows into database".format(len(all_wx)))
    # use generator expression instead of list so we don't convert and then use
    fix_execute(cursor, stmt_insert, all_wx.values)


def write_foreign(cnxn, schema, table, index, fct_insert, cur_df):
    """!
    Write data subset for a foreign key table and then merge the generated foreign keys into data
    @param cnxn Connection to use for query
    @param schema Schema that table resides in
    @param table Table to insert into
    @param index List of index keys for table
    @param fct_insert Function to call to insert into table
    @param cur_df DataFrame with data to insert
    @return DataFrame with original data and merged foreign key data
    """
    qualified_table = '[{}].[{}]'.format(schema, table)
    logging.debug('Writing foreign key data to {}'.format(qualified_table))
    new_index = cur_df.index.names
    cur_df = cur_df.reset_index()
    sub_data = cur_df[index].drop_duplicates().set_index(index)
    fct_insert(cnxn, qualified_table, sub_data)
    # should be much quicker to read out the fk data and do a join on this end
    fkData = pandas.read_sql("SELECT * FROM {}".format(qualified_table), cnxn)
    fkId = [x for x in fkData.columns if x not in index][0]
    fkColumns = [x for x in fkData.columns if x != fkId]
    new_index = [fkId] + [x for x in new_index if x not in fkColumns]
    columns = [fkId] + [x for x in cur_df.columns if x not in fkColumns]
    cur_df = cur_df.merge(fkData)[columns].set_index(new_index)
    return cur_df


def insert_weather(schema, final_table, df, modelFK='Generated', database=None, addStartDate=True):
    """!
    Insert weather data into table and foreign key tables
    @param schema Schema that table exists in
    @param final_table Table to insert into
    @param df DataFrame with data to insert
    @param modelFK Foreign key to use for inserting into DAT_Model table
    @param database Database to insert into
    @param addStartDate Whether or not to add start date for weather to data
    @return None
    """
    def do_insert(cnxn, table, data):
        """Insert and ignore duplicate key failures"""
        stmt_insert = make_insert_statement(table, data.reset_index().columns, False)
        # don't delete and insert without failure
        trans_insert_data(cnxn, data, stmt_insert)
    def do_insert_only(cnxn, table, data):
        """Insert and assume success because no duplicate keys should exist"""
        # rely on deleting from FK table to remove everything from this table, so just insert
        stmt_insert = make_insert_statement(table, data.reset_index().columns)
        trans_insert_data(cnxn, data, stmt_insert)
    # HACK: add column for StartDate for run
    if addStartDate:
        df['StartDate'] = df.reset_index()['ForTime'].min()
    try:
        cnxn = open_local_db(database)
        cur_df = df
        cur_df = write_foreign(cnxn, schema, 'DAT_Location', ['Latitude', 'Longitude'], do_insert, cur_df)
        cur_df = write_foreign(cnxn, schema, 'DAT_Model', ['Model', modelFK, 'StartDate'] if addStartDate else ['Model', modelFK], trans_save_data, cur_df)
        cur_df = write_foreign(cnxn, schema, 'DAT_LocationModel', ['ModelGeneratedId', 'LocationId'], do_insert_only, cur_df)
        logging.debug('Writing data to {}'.format(final_table))
        do_insert_only(cnxn, '[{}].[{}]'.format(schema, final_table), cur_df)
        cnxn.commit()
    finally:
        cnxn.close()


def read_grib(file, match):
    """!
    Read grib data for desired time and field
    @param file Path to source grib2 file to read
    @param match Definition of time and field to look for
    @return DataFrame with data read from file    
    """
    # logging.debug(file)
    CWD = os.path.join(os.path.dirname(file))
    cmd = r'wgrib2-v0.1.9.4\bin\wgrib2.exe'
    bounds = '{}:{} {}:{}'.format(BOUNDS['longitude']['min'],
                                  BOUNDS['longitude']['max'],
                                  BOUNDS['latitude']['min'],
                                  BOUNDS['latitude']['max'])
    args = r'-match "' + match + '" -inv /dev/null -undefine out-box {} -csv'.format(bounds)
    output = r'-'
    # run generated command for parsing data
    run_what = [cmd] + [os.path.basename(file)] + shlex.split(args) + [output]
    logging.debug("Running:\n{}".format(' '.join(run_what)))
    process = subprocess.Popen(run_what,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               creationflags=0x08000000,
                               cwd=CWD)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception('Error processing grib data: ' + stderr)
    # convert into pandas DataFrame
    output = pandas.read_csv(io.BytesIO(stdout),
                             header=None,
                             names=['Generated', 'ForTime', 'Field', 'Level', 'Longitude', 'Latitude', 'Value'],
                             converters=dict((x,
                                              lambda x: None if (not x) else float(x)) \
                                             for x in ['Longitude',
                                                       'Latitude',
                                                       'Value']),
                             parse_dates=['Generated', 'ForTime'],
                             encoding='utf8',
                             date_parser=lambda x: pandas.to_datetime(x, coerce=True))
    variable = output[:1]['Field'][0]
    columns = ['Generated', 'ForTime', 'Longitude', 'Latitude']
    def parse_ensemble(x):
        """!
        Change ensemble name into a number
        @param x Data to parse
        @return Number representing ensemble name
        """
        result = 0 if -1 != x.find('low-res_ctl') else int(x[x.find('.') + 1:])
        return result
    if -1 != variable.find('.'):
        variable = variable[:variable.find('.')]
        output['Member'] = output[['Field']].apply(
            lambda x: parse_ensemble(x[0]), axis=1)
        columns += ['Member']
    output.columns = output.columns.str.replace('Value', variable)
    # HACK: Need to delete possible duplicates so concat works
    output = output.drop_duplicates(columns)
    return output[columns + [variable]].set_index(columns)


def try_remove(file):
    """!
    Delete file but ignore errors if can't while raising old error
    @param file Path to file to delete
    @return None
    """
    try:
        logging.debug("Trying to delete file {}".format(file))
        os.remove(file)
    except:
        pass


def download(get_what, suppress_exceptions=True):
    """!
    Download URL using specified proxy
    @param get_what Array of proxy and URL to use
    @param suppress_exceptions Whether or not return exception instead of raising it
    @return Contents of URL, or exception
    """
    try:
        proxy = get_what[0]
        url = get_what[1]
        if proxy is not None:
            set_proxy(proxy, verbose=False)
        response = urllib2.urlopen(url)
        # logging.debug("Saving {}".format(url))
        return response.read()
    except urllib2.URLError as ex:
        # provide option so that we can call this from multiprocessing and still handle errors
        if suppress_exceptions:
            # HACK: return type and url for exception
            return {'type': type(ex), 'url': url}
        ex.url = url
        raise ex


import multiprocessing

## Multiprocessing pool to use
POOL = None

def download_many(urls, processes=6):
    """!
    Download multiple URLs concurrently using current proxy settings
    @param urls List of multiple URLs to download
    @param processes Number of processes to use for downloading
    @return List of paths that files have been saved to
    """
    global POOL
    if POOL is None:
        POOL = multiprocessing.Pool(processes=processes)
    get_what = zip([CURRENT_PROXY] * len(urls), urls)
    # HACK: use current proxy so we don't do check for proxy and delay this
    # HACK: the get() call means that KeyboardInterrupt actually works
    results = POOL.map_async(download, get_what).get(9999999)
    for i, result in enumerate(results):
        if isinstance(result, dict):
            # HACK: recreate error by trying to open it again
            # if this works this time then everything is fine right?
            results[i] = download(get_what[i], suppress_exceptions=False)
    return results


def split_line(line):
    """!
    Split given line on whitespace sections
    @param line Line to split on whitespace
    @return Array of strings after splitting
    """
    return re.sub(r' +', ' ', line.strip()).split(' ')

