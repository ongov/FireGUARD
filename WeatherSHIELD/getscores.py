"""Get ocean temperature indices and generate percent match scores"""

import pandas as pd
import re
import datetime
import sys
sys.path.append('..\util')
import common
from common import split_line
import pyodbc
import numpy
import sst

#http://www.esrl.noaa.gov/psd/data/correlation/amon.us.data
## Directory to save data to
DIR_DATA = r'data'
## Names for columns
COLUMNS = ['Name','Year','Month','Value']
## Names for index
INDEX = COLUMNS[:3]

## URL for Atlantic Multidecadal Oscillation
URL_AMO = r'http://www.esrl.noaa.gov/psd/data/correlation/amon.us.data'
## URL for Pacific Decadal Oscillation
URL_PDO = r'http://www.ncdc.noaa.gov/teleconnections/pdo/data.csv'
## URL for El Nino Southern Oscillation
URL_ENSO = r'http://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.81-10.ascii'


def save_file(url):
    """!
    Save the given url
    @param url URL to save
    @return Path that URL was saved to
    """
    return common.save_http(DIR_DATA, url)


def read_years(f, min_year, max_year):
    """!
    Read data for given years
    @param f File opened for read
    @param min_year Minimum year to get data for
    @param max_year Maximum year to get data for
    @return Data for years in range
    """
    tmp = pd.DataFrame()
    for year in range(min_year, max_year + 1):
        cols = split_line(f.readline())
        # use first 4 digits because there's ** after some PDO years
        cur_year = int(cols[0][:4])
        assert(year == cur_year)
        values = map(float, cols[1:])
        # print values
        series = pd.Series(values, range(1,len(values)+1))
        tmp[year] = series
    return tmp


def finalize(name, tmp, guard):
    """!
    Clean up and reindex data for final output
    @param name Name to apply to data rows
    @param tmp DataFrame to use
    @param guard Value that indicates missing data
    @return Reindexed data
    """
    tmp = tmp.transpose()
    # get rid of missing numbers
    tmp = tmp.applymap(lambda x: x if x != guard else None)
    columns = ['Year','Month','Value']
    def get_month(month):
        """ Get value for given month and then set value for 'Month' column to match """
        # NOTE: should be replaced with pd.melt()?
        result = tmp[month].reset_index()
        result['Month'] = month
        result.columns = ['Year','Value','Month']
        return result.sort(columns[:2]).set_index(columns[:2])
    result = pd.concat(map(get_month, range(1, 13)))
    print "Index is: {}".format(name)
    result['Name'] = name
    return result.reset_index().sort(['Name'] + columns[:2]).set_index(['Name'] + columns[:2])


def read_AMO(url):
    """!
    Read AMO data from URL
    @param url URL to read from
    @return Atlantic Multidecadal Oscillation data
    """
    filename = save_file(url)
    with open(filename, 'r') as f:
        cols = split_line(f.readline())
        min_year = int(cols[0])
        max_year = int(cols[1])
        # read in data for years
        tmp = read_years(f, min_year, max_year)
        # split into columns
        cols = split_line(f.readline())
        guard = float(cols[0])
        print "Guard value is: {}".format(guard)
        # figure out what value is used for missing data
        cols = split_line(f.readline())
        name = cols[0]
        return finalize(name, tmp, guard)


def read_PDO(url):
    """!
    Read PDO data from URL
    @param url URL to read from
    @return Pacific Decadal Oscillation data
    """
    filename = save_file(url)
    result = pd.read_csv(filename, skiprows=1)
    result['Year'] = result.apply(lambda x: int(x['Date'] / 100), axis=1)
    result['Month'] = result.apply(lambda x: int(x['Date'] % 100), axis=1)
    result = result[['Year', 'Month', 'Value']]
    columns = ['Year','Month','Value']
    result = result.sort(columns[:2]).set_index(columns[:2])
    result['Name'] = 'PDO'
    return result.reset_index().sort(['Name'] + columns[:2]).set_index(['Name'] + columns[:2])


def read_ENSO(url):
    """!
    Read ENSO data from URL
    @param url URL to read from
    @return El Nino Southern Oscillation data
    """
    filename = save_file(url)
    tmp = pd.read_table(filename, sep=r'\s*', engine='python')
    tmp = tmp.set_index(['YR', 'MON'])
    results = []
    def fix_enso(cur, name):
        """ Fix data so that sub-indices are named 'ENSO/<name>' """
        cur = cur.reset_index()
        cur.columns = ['Year', 'Month', 'Value']
        cur['Name'] = 'ENSO/' + name
        cur = cur.reset_index()[COLUMNS]
        return cur.sort(INDEX).set_index(INDEX)
    # we know that for every index there's a value column and then an ANOM value column
    for i in xrange(len(tmp.columns) / 2):
        c = i * 2
        cur = tmp[tmp.columns[c]]
        name = cur.name
        results.append(fix_enso(cur, name))
        # now do the ANOM for this
        cur = tmp[tmp.columns[c + 1]]
        assert('ANOM' == cur.name[:4])
        results.append(fix_enso(cur, name + "/ANOM"))
    return results


def get_standard():
    """!
    Get values for all indices and calculate moving averages and trends
    @return None
    """
    if common.CURRENT_PROXY is not None and common.CURRENT_PROXY.endswith(common.MNR_PROXY):
        common.set_proxy(None)
    common.check_proxy()
    amo = read_AMO(URL_AMO)
    #~ print amo
    # estimate predictions for amo
    amo_mean = amo.reset_index().groupby(['Month']).mean()['Value']
    amo_mean.loc[0] = amo_mean[12]
    amo_mean.loc[13] = amo_mean[1]
    amo_adj = (amo_mean - amo_mean.shift(-1))[0:12]
    amo_last = amo.reset_index().ix[len(amo) - 1]
    cur_date = datetime.datetime(amo_last['Year'], amo_last['Month'], 1)
    amo = amo.reset_index()
    last_value = amo_last['Value']
    for i in xrange(12):
        # HACK: move ahead a month but stay on the 1st
        cur_date = cur_date + datetime.timedelta(days=32)
        cur_date = datetime.datetime(cur_date.year, cur_date.month, 1)
        #~ value = last_value + amo_adj[cur_date.month]
        value = amo_adj[cur_date.month]
        amo.loc[len(amo)] = ['AMO', cur_date.year, cur_date.month, value]
        last_value = value
    pdo = read_PDO(URL_PDO)
    #~ print pdo
    result = pd.concat([amo, pdo])
    enso = read_ENSO(URL_ENSO)
    #~ print enso
    result = pd.concat([result] + enso)
    #~ print result
    # add in predictions for ENSO
    enso_future = sst.load().reset_index()
    enso_future['Index'] = enso_future.apply(lambda x: 'ENSO/{}/ANOM'.format(x['Index'].upper()), axis=1)
    ef_melt = pd.melt(enso_future, id_vars=['Index'])
    ef_melt['Year'] = ef_melt.apply(lambda x: x['Date'].year, axis=1)
    ef_melt['Month'] = ef_melt.apply(lambda x: x['Date'].month, axis=1)
    ef_melt = ef_melt[['Index', 'Year', 'Month', 'value']]
    ef_melt.columns = ['Name', 'Year', 'Month', 'Value']
    ef_melt = ef_melt.set_index(INDEX)
    result = pd.concat([result, ef_melt])
    result = result.reset_index().sort(INDEX).set_index(INDEX)
    # remove all NaN values by querying (HACK: NaN != NaN)
    result = result.query('Value == Value')
    #~ common.save_data('[INPUTS].[DAT_Climate]', result)
    # now do the analysis
    def get_index(name):
        """ Retrieve data related to an index by name for it """
        return result.reset_index().query('Name == "{}"'.format(name)).set_index(INDEX)
    def calc_MA(data, months):
        """ Calculate moving average on data using number of months as window for averaging """
        tmp = data
        for i in xrange(1, months):
            tmp = tmp + data.shift(i)
        tmp = tmp / months
        return tmp
    # PDO
    pdo = get_index('PDO')
    # PDO uses an average over the last 4 months
    pdo_MA = calc_MA(pdo, 4)
    # compares current to 2 months ago
    pdo_trend = pdo_MA - pdo_MA.shift(2)
    # AMO
    amo = get_index("AMO")
    # AMO uses an average over the last 8 months
    amo_MA = calc_MA(amo, 8)
    # compares current to last month
    amo_trend = amo_MA - amo_MA.shift(1)
    # ENSO uses the ANOM value for NINO3.4 column
    enso = get_index('ENSO/NINO3.4/ANOM')
    # ENSO uses 2 month average
    enso_MA = calc_MA(enso, 2)
    # compares current to last month
    enso_trend = enso_MA - enso_MA.shift(1)
    # # get the last year of each index and check they're for the same period
    # pdo_current = pdo.tail(12)
    # amo_current = amo.tail(12)
    # enso_current = enso.tail(12)
    # assert(pdo_current.index[0][1:] == amo_current.index[0][1:] == enso_current.index[0][1:])
    def find_diff(val, year, range):
        """ Find the difference in values between desired year and all other years """
        min_year = val.sort().index.min()[1]
        max_year = val.sort().index.max()[1]
        print min_year, max_year
        cur = val.query('Year == {}'.format(year)) 
        print cur
        val_diff = val - numpy.tile(cur.values, (max_year - min_year + 1, 1))
        result = val_diff.apply(lambda x: (1 - abs(x) / range))
        return result
    def by_year(df, query):
        """ Group data by year """
        return df.reset_index().groupby(['Year']).count().query(query).index.values
    def find_score(cur, cur_MA, cur_trend, year):
        """ Find the score for the current index compared to the current year """
        # find years that are missing any values from trend
        incomplete = map(int, by_year(cur_trend, 'Value < 12'))
        print incomplete
        # replace ] with ,) so that it's always a list even if single value
        no_incomplete = 'Year not in {}'.format(incomplete).replace('[', '(').replace(']', ',)')
        cur_trend.query(no_incomplete)
        # divide difference by range to scale according to what has happened in past
        range = max(cur.values) - min(cur.values)
        cur_MA_diff = find_diff(cur_MA.query(no_incomplete), year, range)
        cur_trend_diff = find_diff(cur_trend.query(no_incomplete), year, range)
        score = cur_MA_diff * 0.75 + cur_trend_diff * 0.25
        return score
    def score_against(year):
        """ Get a total score for all other years compared to desired year """
        pdo_score = find_score(pdo, pdo_MA, pdo_trend, year)
        amo_score = find_score(amo, amo_MA, amo_trend, year)
        enso_score = find_score(enso, enso_MA, enso_trend, year)
        def get_raw(val):
            """ Rename and reindex data so that columns are named identically """
            cols = ['Year', 'Month', 'Value']
            return val.reset_index()[cols].set_index(cols[:2])
        total = get_raw(enso_score) * 0.5 + get_raw(pdo_score) * 0.35 + get_raw(amo_score) * 0.15
        total = total.query('Value == Value')
        total['Against'] = year
        return total.reset_index().set_index(['Year', 'Month', 'Against'])
    # enso is the most restrictive, so use its set of years
    results = []
    for year in map(int, by_year(enso_trend, 'Value == 12')):
        print 'Checking against {}'.format(year)
        results.append(score_against(year))
    result = pd.concat(results)
    def save_comparison(year):
        """ Save calculated comparison to csv """
        for_year = result.query('Against == {}'.format(year)).query('Year != {}'.format(year)).reset_index()
        out = for_year.sort(['Month','Value'], ascending=(True, False)).set_index(['Against', 'Month'])
        out.to_csv(r'output/match{}.csv'.format(year))
        out.reset_index()[['Month', 'Year', 'Value']].pivot(index='Year', columns='Month').to_csv(r'output/{}.csv'.format(year))
    # do comparison for years and save them
    #~ for year in xrange(2010, 2016):
        #~ save_comparison(year)
    save_comparison(datetime.datetime.now().year)

if __name__ == "__main__":
    get_standard()
