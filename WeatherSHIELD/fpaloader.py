"""Load Forecast Production Assistant (FPA) data"""

from weatherloader import WeatherLoader
import pandas
import datetime
import sys
sys.path.append('..\util')
import common
from common import split_line
from io import StringIO
import urllib2
import logging
import numpy
import os

## Grid to load points from
GRID_FILE = common.CONFIG.get('FireGUARD', 'fpa_locations_grid')

def load_locations():
    """!
    Load location data that was used for FPA points
    @return DataFrame with location data for points
    """
    def make_data(line):
        cols = split_line(line)
        name = cols[0]
        latitude = cols[1]
        fixed_latitude = float(latitude[:-1])
        if latitude[-1] == 'S':
            fixed_latitude *= -1
        longitude = cols[2]
        fixed_longitude = float(longitude[:-1])
        if longitude[-1] == 'W':
            fixed_longitude *= -1
        number = int(cols[4].replace('"', ''))
        return [name, fixed_latitude, fixed_longitude, number]
    with open(GRID_FILE, 'r') as f:
        lines = [line for line in f]
        columns = ['Name', 'Latitude', 'Longitude', 'Number']
        return pandas.DataFrame(map(make_data, lines),
                                columns=columns)

def load_data(data):
    """!
    Load data from given string
    @param data String to use as input
    @return DataFrame with loaded data
    """
    if not data:
        return None
    columns = ['Name',
               'MinutesOfRain',
               'ForDate',
               'ForHour',
               'UNK1',
               'Generated',
               'UNK2',
               'TMP',
               'RH',
               'WD',
               'WS',
               'APCP']
    fake_file = StringIO(unicode(data, 'utf-8'))
    df = pandas.read_csv(fake_file,
                          names=columns,
                          parse_dates=["ForDate", "Generated"],
                          date_parser=lambda x: pandas.to_datetime(x, coerce=True))
    def make_date(x):
        # combine date with hours
        return datetime.datetime.combine(x['ForDate'].date(), datetime.time(hour=x['ForHour']))
    # print df.dtypes
    df['ForTime'] = df[['ForDate', 'ForHour']].apply(make_date, axis=1)
    # HACK: somehow we ended up with duplicate points in the files we used in FPA
    # NOTE: no index is set right now - otherwise would need to reset_index()
    return df.drop_duplicates()


class FPALoader(WeatherLoader):
    """Load weather from FPA data that the weather office produces"""
    def get_file_name(self, for_run, basename):
        """!
        Create file name from mask and time
        @param for_run Run to generate file name from
        @param basename Base name to use in file name
        @return Path to save run data to
        """
        return os.path.join(self.DIR_DATA, 'FPA_{}_{}'.format(for_run.strftime('%Y%m%d%H%M'), basename))
    def read_file(self, filename):
        """!
        Read entire contents of file into string
        @param filename Path to file to read
        @return String with entire contents of file
        """
        with open(filename, 'r') as in_file:
            return in_file.read()
    def save_and_read(self, url):
        """!
        Save a URL and then return the contents of the saved file
        @param url URL to save from
        @return String with entire contents of downloaded file
        """
        ## Name of file to save to
        filename = os.path.join(self.DIR_DATA, os.path.basename(url))
        # HACK: set filename but then set it again for no reason if we need to download
        if not self.no_download:
            filename = common.save_http(self.DIR_DATA, url)
        return self.read_file(filename)
    def load_dumped_records(self, year=None, force=False):
        """!
        Load dump of old records
        @param year Year to load data from, or None to load all past years
        @param force Whether or not to load data if it is already in database
        @return None
        """
        import glob
        files = glob.glob(self.DIR_DATA + '/fpadump_*.csv')
        all_wx = []
        for filename in files:
            logging.debug('Loading weather from {}'.format(filename))
            wx = pandas.read_csv(
                        filename,
                        parse_dates=['ForTime', 'Generated']
                    )
            all_wx.append(wx)
        if 0 == len(all_wx):
            return
        wx = pandas.concat(all_wx).drop_duplicates()
        index = ['Generated', 'ForTime', 'Model', 'Member', 'Latitude', 'Longitude']
        wx = wx.sort(index)
        for generated in wx['Generated'].unique():
            cur_wx = wx[wx['Generated'] == generated]
            cur_wx = cur_wx.set_index(index)
            for_run = pandas.to_datetime(generated)
            if not year or for_run.year == year:
                self.save_if_required(cur_wx, force)
    def load_past_records(self, year=None, force=False):
        """!
        Determine which past run files we have and load them
        @param year Year to load data from, or None to load all past years
        @param force Whether or not to load data if it is already in database
        @return None
        """
        import glob
        files = glob.glob(self.DIR_DATA + '/FPA_*.csv')
        def file_run(file):
            start = file.index('_') + 1
            end = file.index('_', start)
            return file[start:end]
        runs = list(set([file_run(d) for d in files]))
        # sort so we do the dates chronologically
        runs.sort()
        for run in runs:
            for_run = datetime.datetime.strptime(run, '%Y%m%d%H%M')
            if not year or for_run.year == year:
                self.load_run(for_run, force)
    def load(self, force=False):
        """!
        Load data
        @param force Whether or not to load data if it is already in database
        @return Timestamp for loaded run
        """
        loaded_files = map(self.save_and_read, self.urls)
        for_run = self.load_from_results(loaded_files, force)
        # now that we've loaded everything save a backup of these files
        for filename in map(lambda x: os.path.join(self.DIR_DATA, os.path.basename(x)), self.urls):
            copyname = self.get_file_name(for_run, os.path.basename(filename))
            logging.debug("Saving {} to {}".format(filename, copyname))
            common.copy_file(filename, copyname)
        return for_run
    def load_run(self, for_run, force=False):
        """!
        Load from specific set of files instead of current live version
        @param for_run Run to load data for
        @param force Whether or not to load data if it is already in database
        @return Timestamp for loaded run
        """
        loaded_files = map(lambda x: self.read_file(self.get_file_name(for_run, os.path.basename(x))), self.urls)
        return self.load_from_results(loaded_files, force)
    def load_from_results(self, results, force=False):
        """!
        Load data from a list of files
        @param results List of paths for files that represent data
        @param force Whether or not to load data if it is already in database
        @return None
        """
        stns = load_locations()
        index = ['ForTime', 'Model', 'Member', 'Latitude', 'Longitude']
        columns = ['Generated', 'TMP', 'RH', 'WS', 'WD', 'APCP']
        loaded = []
        best_date = None
        missing = set([])
        def add_sets(a, b):
            return set(list(a) + list(b))
        raw_loaded = []
        for i, result in enumerate(results):
            raw_data = load_data(result)
            if raw_data is None:
                logging.warning('Empty input file for day {}'.format(i))
            else:
                cur_date = pandas.Timestamp(raw_data.reset_index()['Generated'].values[0])
                logging.debug('Checking cur_date {} against {}'.format(cur_date, best_date))
                # print type(cur_date), cur_date
                # print type(best_date), best_date
                if best_date is None or cur_date.date() > best_date.date():
                    # previous data was from before this date so get rid of it
                    if best_date is not None:
                        logging.debug('Disposing of older data since {} is newest so far'.format(cur_date))
                    best_date = cur_date
                    raw_loaded = []
                # do if instead of elif so if we just set it then it still works
                if cur_date.date() == best_date.date():
                    # we want to keep the maximum date
                    if cur_date > best_date:
                        best_date = cur_date
                    # NOTE: if we compare to the base set of stations this should work
                    difference = set([x for x in stns['Name'].values if x not in raw_data['Name'].values])
                    if len(difference) > 0:
                        logging.warning('Data missing for day {}: {}'.format(self.for_days[i], difference))
                        missing = add_sets(missing, difference)
                    raw_loaded.append(raw_data)
                else:
                    logging.debug('Not using outdated forecast for {}'.format(cur_date))
                    # else this date is worse than the current best
                    # else cur_date is the same as best_date
        # HACK: change these here so that they're set properly at the end too
        index = columns[:1] + index
        columns = columns[1:]
        for raw_data in raw_loaded:
            df = raw_data.merge(stns)
            # HACK: remove all stations that are missing for any day
            df = df[~df['Name'].isin(missing)]
            df['Model'] = 'AFFES'
            df['Member'] = 0
            df = df.set_index(index)[columns]
            loaded.append(df)
        wx = pandas.concat(loaded)
        # wx = stns.merge(pandas.concat(map(load_data, results)))
        wx = wx.reset_index().sort(index)
        # override the Generated date for all items since if we pushed an update today
        # and didn't change them then that means we can consider them to be as up to date
        # as the latest version
        wx['Generated'] = best_date
        wx = wx.set_index(index)[columns]
        return self.save_if_required(wx, force)
    def save_if_required(self, wx, force=False):
        """!
        Save data if not in database already, unless forced
        @param wx Data to save into database if not already present
        @param force Whether or not to load data if it is already in database
        @return Timestamp for loaded run
        """
        # HACK: somehow still getting duplicates
        index = wx.index.names
        # NOTE: need to reset_index() because otherwise only compares wx values
        wx = wx.reset_index().drop_duplicates().set_index(index)
        # HACK: Timestamp format is nicer than datetime's
        for_run = wx.reset_index()['Generated'].max()
        # want to put the data into the database for the start date but check if it exists based on for_run
        start_date = wx.reset_index()['ForTime'].min()
        dbname = common.get_database(start_date)
        # if at any point for_run is already in the database then we're done
        if not force:
            logging.debug('Checking if data is already present for {} model generated at {}'.format(self.name, for_run))
            exists = self.check_exists(for_run, dbname)
            if exists:
                logging.debug('Data already loaded - aborting')
                return pandas.Timestamp(for_run)
        self.save_data(wx, dbname)
        # return the run that we ended up loading data for
        return for_run
    def load_records(self, max_retries=5):
        """!
        Load the latest records using the specified interval to determine run
        @param max_retries Maximum number of times to retry before failing
        @return Timestamp for loaded run
        """
        # HACK: this is inside the intranet so make sure we're not using a proxy if we're in the intranet
        if common.CURRENT_PROXY is not None and common.CURRENT_PROXY.endswith(common.MNR_PROXY):
            common.set_proxy(None)
        try:
            # get_files(get_nearest_run(6), 'reg10km')
            return self.load()
        except urllib2.HTTPError as ex:
            logging.critical(ex)
            # HACK: we set the URL in the place the error originated from
            logging.critical(ex.url)
    def __init__(self, no_download=False):
        """!
        Instantiate class
        @param no_download Whether or not to not download data
        """
        super(FPALoader, self).__init__(name='AFFES',
                                        for_days=range(1, 6),
                                        no_download=no_download)
        ## Base URL to save from
        site = common.CONFIG.get('FireGUARD', 'url_agency_wx')
        self.urls = map(lambda d: site + 'Day{}.csv'.format(d), self.for_days)
        


if __name__ == "__main__":
    FPALoader().load_records()
