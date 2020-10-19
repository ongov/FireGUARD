"""Load long range month matches from web site"""

import pandas
import re
import datetime
import sys
sys.path.append('..\util')
import common
from common import split_line
import pyodbc
import numpy
import os
import logging

## Folder to save to
DIR_DATA = r'data/longrange'
## Columns to use
COLUMNS = ['Name','Year','Month','Value']
## Index columns
INDEX = COLUMNS[:3]
# using product created by weather office now
## Root URL for downloading
site = common.CONFIG.get('FireGUARD', 'url_agency_wx')
## URL for downloading
url = site + common.CONFIG.get('FireGUARD', 'url_agency_wx_longrange')

def save_file(url):
    """!
    Save the given url
    @param url URL to save
    @return Path that URL was saved to
    """
    return common.save_http(DIR_DATA, url)

def get_file_name(for_run):
    """!
    Generates name to use for file with given run data
    @param for_run datetime for run
    @return File name that run data should be saved to
    """
    return os.path.join(DIR_DATA, 'longrange_{}.csv'.format(for_run.strftime('%Y%m%d%H%M')))

def get_standard(force=False):
    """!
    Save long range match data
    @param force Whether or not to save if file already exists
    @return Timestamp for saved data
    """
    # HACK: this is inside the intranet so make sure we're not using a proxy if we're in the intranet
    if common.CURRENT_PROXY is not None and common.CURRENT_PROXY.endswith(common.MNR_PROXY):
        common.set_proxy(None)
    logging.debug('Saving long range forecast matches')
    filename = save_file(url)
    filetime = os.path.getmtime(filename)
    for_run = datetime.datetime.fromtimestamp(filetime)
    # HACK: get rid of microseconds because database conversion fails
    for_run = for_run.replace(microsecond=0)
    # copy file to dated file name so that we can load them later on
    common.copy_file(filename, get_file_name(for_run))
    return load_file(for_run, force)

def load_file(for_run, force=False):
    """!
    Load data for a given run into the database
    @param for_run datetime to load data for
    @param force Whether or not to save if file already exists
    @return Timestamp for run data that was loaded
    """
    if not force:
        logging.debug('Checking if data is already present for long range matches generated at {}'.format(for_run))
        exists = check_exists(for_run)
        if exists:
            logging.debug('Data already loaded - aborting')
            return pandas.Timestamp(for_run)
    filename = get_file_name(for_run)
    df = pandas.read_csv(filename)
    # throw out everything except years and months
    df = df[df.columns[:13]]
    # change months into numbers
    df.columns = ['Year'] + range(1, 13)
    df = pandas.melt(df,
                        id_vars=['Year'],
                        var_name='Month',
                        value_name='Value')
    # remove NaN rows
    df = df.query('Value == Value')
    # get warnings later if we don't set this
    df.is_copy = False
    # convert to ratio while checking for % and other possible inputs
    def fix_ratio(x):
        if isinstance(x, str):
            if '%' == x[-1]:
                x = int(x[:-1])
            x = int(x)
        return x if 1 >= x else x / 100.0
    #~ fix_ratio(df.values[0][2])
    df['Value'] = df['Value'].apply(fix_ratio)
    df['Generated'] = pandas.to_datetime(for_run)
    #~ df['Generated'] = df['Generated'].astype('datetime64[s]')
    df = df.set_index(['Generated', 'Year', 'Month'])
    database = 'HINDCAST'
    schema = 'HINDCAST'
    final_table = 'DAT_HistoricMatch'
    def do_insert_only(cnxn, table, data):
        """Insert and assume success because no duplicate keys should exist"""
        # rely on deleting from FK table to remove everything from this table, so just insert
        stmt_insert = common.make_insert_statement(table, data.reset_index().columns)
        common.trans_insert_data(cnxn, data, stmt_insert)
    try:
        cnxn = common.open_local_db(database)
        cur_df = df
        cur_df = common.write_foreign(cnxn, schema, 'DAT_Historic', ['Generated'], common.trans_save_data, cur_df)
        logging.debug('Writing data to {}'.format(final_table))
        do_insert_only(cnxn, '[{}].[{}]'.format(schema, final_table), cur_df)
        cnxn.commit()
    finally:
        cnxn.close()
    return pandas.Timestamp(for_run)

def check_exists(for_run):
    """!
    Check if data for given Generated time already exists
    @param for_run datatime to check database for run data from
    @return Whether or not data exists in database for given run
    """
    try:
        cnxn = common.open_local_db('HINDCAST')
        df = pandas.read_sql('SELECT * FROM [HINDCAST].[DAT_Historic]', cnxn)
    finally:
        cnxn.close()
    return 1 == len(df.query('Generated == \'{}\''.format(for_run)))


def load_past_records(year=None, force=False):
    """!
    Determine which past run files we have and load them
    @param year Year to load, or None to load all past years
    @param force Whether or not to load if data already exists
    @return None
    """
    import glob
    files = glob.glob(os.path.join(DIR_DATA, 'longrange_*.csv'))
    def file_run(file):
        start = file.index('_') + 1
        end = file.index('.', start)
        return file[start:end]
    runs = list(set([file_run(d) for d in files]))
    # sort so we do the dates chronologically
    runs.sort()
    for run in runs:
        for_run = datetime.datetime.strptime(run, '%Y%m%d%H%M')
        if year is None or for_run.year == year:
            load_file(for_run, force)


if __name__ == "__main__":
    get_standard()

