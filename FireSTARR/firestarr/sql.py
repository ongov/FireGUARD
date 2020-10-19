"""SQL and database functions"""

import sys
sys.path.append('..\util')
import common
import pyodbc
import pandas
import numpy
import datetime
from dateutil.parser import parse

def get_dfoss_connection():
    """!
    Return connection to DFOSS database
    @return pyodbc connection to DFOSS database
    """
    return pyodbc.connect(common.CONFIG.get('FireGUARD', 'dfoss_connection'))


def read_remote(stmt):
    """!
    Execute query on DFOSS database
    @param stmt SQL query
    @return Dataframe with results
    """
    cnxn = None
    try:
        cnxn = get_dfoss_connection()
        return pandas.read_sql(stmt, cnxn)
    finally:
        if cnxn:
            cnxn.close()


def get_current_fires():
    """!
    Get fires that are currently active from DFOSS
    @return Current fires from DFOSS
    """
    stmt_select = r'''SELECT
    f.FIREID,
    c.ORGUNITCODE || TO_CHAR(f.FIRESEQ, '000') AS FIRENAME,
    f.LATITUDE,
    f.LONGITUDE,
    f.CONFIRMDATE,
    f.SMOKECOLUMN,
    (SELECT s.CURRENTSIZE
        FROM FIRESTATUS s
        WHERE s.FIREID = f.FIREID
            AND s.STATUSDATE = (
                    SELECT MAX(s2.STATUSDATE)
                    FROM FIRESTATUS s2
                    WHERE s2.FIREID = f.FIREID)
    ) as CURRENTSIZE,
    (SELECT s.CONDITION
        FROM FIRESTATUS s
        WHERE s.FIREID = f.FIREID
            AND s.STATUSDATE = (
                    SELECT MAX(s2.STATUSDATE)
                    FROM FIRESTATUS s2
                    WHERE s2.FIREID = f.FIREID)
    ) as CONDITION
FROM
    (SELECT *
    FROM FIRE f2
    WHERE f2.FIREID NOT IN 
        (SELECT DISTINCT FIREID
        FROM FIRESTATUS s
        WHERE CONDITION = 'OUT'
            AND f2.FIRETYPE <> 'PB')) f
    LEFT JOIN CT_ORGUNIT c ON c.ORGUNIT=f.ORGUNIT
WHERE f.FIRETYPE <> 'PB'
'''
    index = ['FIREID']
    delete_all = True
    # need to fix longitude because they're all positive even though they're in the west
    df = read_remote(stmt_select).set_index(index)
    df['LONGITUDE'] = df['LONGITUDE'].apply(lambda x: -abs(x))
    return df

def get_all_fires(fire_mask):
    """!
    Get all fires that match the given mask from DFOSS
    @param fire_mask Mask to match
    @return Dataframe with all matching fires
    """
    stmt_select = r'''SELECT
    f.FIREID,
    c.ORGUNITCODE || TO_CHAR(f.FIRESEQ, '000') AS FIRENAME,
    f.LATITUDE,
    f.LONGITUDE,
    f.CONFIRMDATE,
    f.SMOKECOLUMN,
    (SELECT s.CURRENTSIZE
        FROM FIRESTATUS s
        WHERE s.FIREID = f.FIREID
            AND s.STATUSDATE = (
                    SELECT MIN(s2.STATUSDATE)
                    FROM FIRESTATUS s2
                    WHERE s2.FIREID = f.FIREID)
            AND ROWNUM = 1
    ) as CURRENTSIZE,
    (SELECT s.CONDITION
        FROM FIRESTATUS s
        WHERE s.FIREID = f.FIREID
            AND s.STATUSDATE = (
                    SELECT MIN(s2.STATUSDATE)
                    FROM FIRESTATUS s2
                    WHERE s2.FIREID = f.FIREID)
            AND ROWNUM = 1
    ) as CONDITION
FROM
    (SELECT *
    FROM FIRE f2
    WHERE f2.FIRETYPE <> 'PB') f
    LEFT JOIN CT_ORGUNIT c ON c.ORGUNIT=f.ORGUNIT
WHERE f.FIRETYPE <> 'PB'
'''
    if fire_mask and len(fire_mask) > 0:
        stmt_select += "AND\n ORGUNITCODE LIKE '%" + fire_mask[:3] + "%'"
        if len(fire_mask) > 3:
            stmt_select += ' AND f.FIRESEQ =' + str(int(fire_mask[3:]))
    index = ['FIREID']
    delete_all = True
    # need to fix longitude because they're all positive even though they're in the west
    df = read_remote(stmt_select).set_index(index)
    df['LONGITUDE'] = df['LONGITUDE'].apply(lambda x: -abs(x))
    return df


def get_fires_by_date(fire_mask, for_date):
    """!
    Get fires that are active as of a certain date
    @param fire_mask Mask to find matching fires for
    @param for_date Date to find fires that are active on
    @return Dataframe with matching fires
    """
    d = parse(for_date)
    stmt_select = r'''SELECT
    f.FIREID,
    c.ORGUNITCODE || TO_CHAR(f.FIRESEQ, '000') AS FIRENAME,
    f.LATITUDE,
    f.LONGITUDE,
    f.CONFIRMDATE,
    f.SMOKECOLUMN,
    c3.CONDITION,
    c3.CURRENTSIZE
FROM
    (
        SELECT *
        FROM FIRE f2
        WHERE f2.FIRETYPE <> 'PB'
        AND f2.CONFIRMDATE <= TO_DATE('{0}', 'YYYY-MM-DD')
    ) f
    LEFT JOIN (
        SELECT FIREID, CONDITION, CURRENTSIZE
        FROM FIRESTATUS s
        WHERE s.STATUSDATE <= TO_DATE('{0}', 'YYYY-MM-DD')
            AND s.STATUSDATE=(
                SELECT MAX(STATUSDATE)
                FROM FIRESTATUS s2
                WHERE s2.FIREID=s.FIREID
                    AND s2.STATUSDATE <= TO_DATE('{0}', 'YYYY-MM-DD')
            )
    ) c3 ON c3.FIREID=f.FIREID
    LEFT JOIN CT_ORGUNIT c ON c.ORGUNIT=f.ORGUNIT
WHERE CONDITION <> 'OUT'
    AND f.FIRETYPE <> 'PB'
'''
    if fire_mask and len(fire_mask) > 0:
        stmt_select += "\nAND ORGUNITCODE LIKE '%" + fire_mask[:3] + "%'"
        if len(fire_mask) > 3:
            stmt_select += ' AND f.FIRESEQ =' + str(int(fire_mask[3:]))
    stmt_select += '\nORDER BY FIRENAME'
    index = ['FIREID']
    delete_all = True
    # need to fix longitude because they're all positive even though they're in the west
    # HACK: add a day since we want everything up to midnight
    fixed_date = (parse(for_date) + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    df = read_remote(stmt_select.format(fixed_date)).set_index(index)
    df['LONGITUDE'] = df['LONGITUDE'].apply(lambda x: -abs(x))
    return df
