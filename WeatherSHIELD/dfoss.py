"""DFOSS database access and queries"""

import logging
import pyodbc
import pandas
import numpy
import sys
sys.path.append('..\util')
import common
from common import make_insert_statement
import datetime

# HACK: can only load current year data from live server
## Name of database to load data into
DBNAME = 'DFOSS_{}'.format(datetime.datetime.now().year)
## Schema that tables exist in
SCHEMA = r'[INPUTS]'

def get_dfoss_connection():
    """!
    Return connection to DFOSS database
    @return pyodbc connection to DFOSS database
    """
    return pyodbc.connect(common.CONFIG.get('FireGUARD', 'dfoss_connection'))


def read_remote(stmt):
    """!
    Execute statement and return DataFrame with results
    @param stmt SQL statement to execute
    @return DataFrame with SQL statement results
    """
    cnxn = None
    try:
        cnxn = get_dfoss_connection()
        return pandas.read_sql(stmt, cnxn)
    except:
        print("Couldn't open connection")
        return None
    finally:
        if cnxn:
            cnxn.close()


def copy_table(stmt_select, local_table, index, delete_all=False):
    """!
    Copy contents of remote table to local database
    @param stmt_select SQL statement for reading data
    @param local_table Table in local database to insert into
    @param index Index for data that gets read
    @param delete_all Whether or not to clear entire table before adding data
    @return None
    """
    # insert_data(read_remote(stmt_select), local_table)
    # need to set index or it screws up and tries to insert 'Index' column
    result = read_remote(stmt_select)
    if result is not None:
        common.save_data(SCHEMA + '.' + local_table, result.set_index(index), delete_all, DBNAME)


def copy_ct_wstn():
    """!
    Copy CT_WSTN (code table for weather stations)
    @return None
    """
    stmt_select = r'select * from ct_wstn'
    local_table = r'[CT_WSTN]'
    index = ['WSTNCODE']
    delete_all = True
    # copy_table(stmt_select, local_table, index, True)
    # need to fix longitude because they're all positive even though they're in the west
    result = read_remote(stmt_select)
    if result is None:
        return
    df = result.set_index(index)
    df['LONGITUDE'] = df['LONGITUDE'].apply(lambda x: -abs(x))
    common.save_data(SCHEMA + '.' + local_table, df, delete_all, DBNAME)


def copy_wforecast(copy_all=False):
    """!
    Load forecast weather data
    @param copy_all Whether or not to load all data or just today's
    @return None
    """
    # get forecasts that were made today for today
    copy_table(r'select * from wforecast WHERE forecastdatetime <= TRUNC(sysdate + 1)' +
                    (''  if copy_all else ' AND createddate >= TRUNC(sysdate)'),
               r'[WFORECAST]',
               ['FORECASTID'],
               copy_all)


def copy_wobserv(copy_all=False):
    """!
    Load observed weather data
    @param copy_all Whether or not to load all data or just today's
    @return None
    """
    copy_table(r'select * from wobserv' +
                    (''  if copy_all else ' WHERE createddate >= TRUNC(sysdate - 1)'),
               r'[WOBSERV]',
               ['WOBSERVID'],
               copy_all)


def get_fires():
    """!
    Load fire data
    @return None
    """
    stmt_select = r'''SELECT
    f.FIREID,
    c.ORGUNITCODE || TO_CHAR(f.FIRESEQ, '000') AS FIRENAME,
    f.LATITUDE,
    f.LONGITUDE
FROM
    (SELECT *
    FROM FIRE f2
    WHERE f2.FIREID NOT IN 
        (SELECT DISTINCT FIREID
        FROM FIRESTATUS s
        WHERE CONDITION = 'OUT')) f
    LEFT JOIN CT_ORGUNIT c ON c.ORGUNIT=f.ORGUNIT
'''
    local_table = r'[ACTIVEFIRE]'
    index = ['FIREID']
    delete_all = True
    # need to fix longitude because they're all positive even though they're in the west
    result = read_remote(stmt_select)
    if result is None:
        return
    df = result.set_index(index)
    df['LONGITUDE'] = df['LONGITUDE'].apply(lambda x: -abs(x))
    common.save_data(local_table, df, delete_all, DBNAME)


def load():
    """!
    Load data for all tables
    @return None
    """
    copy_ct_wstn()
    copy_wforecast()
    copy_wobserv()
    get_fires()


def load_past_records():
    """!
    Load all data for current year
    @return None
    """
    copy_ct_wstn()
    copy_wforecast(True)
    copy_wobserv(True)


if __name__ == "__main__":
    load()
