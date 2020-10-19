from weatherloader import WeatherLoader
import datetime
import urllib2

import glob
import sys
sys.path.append('..\util')
import common
import os
import pandas
import logging
import socket

class GribLoader(WeatherLoader):
    """Loads NAEFS data from NOMADS"""
    # Provide mapping between fields we're looking for and the file names that contain them
    class WeatherIndex(object):
        """Simple class for mapping indices to lookup data"""
        def __init__(self, name, grib_field, layer):
            """!
            An index in the grib data that gets processed
            @param self Pointer to this
            @param name Name of the index
            @param grib_field Field in the grib data to read index for
            @param layer Layer in the grib data to read for index
            """
            ## Name of the index
            self.name = name
            ## Field in the grib data to read for index
            self.grib_field = grib_field
            ## Layer in the grib data to read for index
            self.layer = layer
    ## The indices that get processed when loading weather
    indices = {
        'TMP': WeatherIndex('TMP', r':TMP:2 m above ground:', 'lev_2_m_above_ground'),
        'UGRD': WeatherIndex('UGRD', r':UGRD:10 m above ground:', 'lev_10_m_above_ground'),
        'VGRD': WeatherIndex('VGRD', r':VGRD:10 m above ground:', 'lev_10_m_above_ground'),
        'RH': WeatherIndex('RH', r':RH:2 m above ground:', 'lev_2_m_above_ground'),
        'APCP': WeatherIndex('APCP', r':APCP:surface:', 'lev_surface')
    }
    def read_grib(self, for_run, for_date, name):
        """!
        Read grib data for desired time and field
        @param self Pointer to this
        @param for_run Which run of model to use
        @param for_date Which date of model to use
        @param name Name of index to read
        @return Index data as a pandas dataframe
        """
        def get_match_files(weather_index):
            """!
            Generate URL containing data
            @param weather_index WeatherIndex to get files for
            """
            # Get full url for the file that has the data we're asking for
            diff = for_date - for_run
            real_hour = (diff.days * 24) + (diff.seconds / 60 / 60)
            file = self.mask.format('{}', for_run.hour, real_hour)
            var = r'&{}=on&var_{}=on'.format(weather_index.layer, weather_index.name)
            subregion_mask = r'&subregion=&leftlon={}&rightlon={}&toplat={}&bottomlat={}'
            subregion = subregion_mask.format(common.BOUNDS['longitude']['min'],
                                              common.BOUNDS['longitude']['max'],
                                              common.BOUNDS['latitude']['max'],
                                              common.BOUNDS['latitude']['min'])
            date = for_run.strftime(r'%Y%m%d')
            time = for_run.strftime(r'%H')
            dir = self.dir.format(date, time)
            url = r'{}{}{}{}{}{}'.format(self.host, self.script, file, var, subregion, dir)
            def get_local_name(partial_url):
                """!
                Return file name that will be saved locally from partial_url
                @param partial_url Partial url to use for determining name
                @return Path to save to locally when using URL to retrieve
                """
                save_as = '{}_{}{}_{}_{:03d}'.format(self.name, date, time, weather_index.name, real_hour)
                return os.path.join(self.DIR_DATA, save_as)
            def save_file(partial_url):
                """!
                Save the given url
                @param partial_url Partial url to use for determining name
                @return Path saved to when using URL to retrieve
                """
                out_file = get_local_name(partial_url)
                if os.path.isfile(out_file):
                    # HACK: no timestamp so don't download if exists
                    return out_file
                logging.debug("Downloading {}".format(out_file))
                def generate_member(member):
                    member_name = r'ge{}{:02d}'.format('c' if member == 0 else 'p', member)
                    url = partial_url.format(member_name)
                    return url
                urls = map(generate_member, xrange(0, 21))
                results = common.download_many(urls)
                assert(21 == len(results))
                try:
                    # logging.debug("Writing file")
                    with open(out_file, "wb") as f:
                        for result in results:
                            f.write(result)
                except:
                    # get rid of file that's there if there was an error
                    common.try_remove(out_file)
                    raise
                return out_file
            if self.no_download:
                # return file that would have been saved without actually trying to save it
                return get_local_name(url)
            return common.try_save(save_file, url)
        weather_index = self.indices[name]
        file = get_match_files(weather_index)
        result = common.read_grib(file, weather_index.grib_field)
        index = result.index.names
        columns = result.columns
        result = result.reset_index()
        result['Model'] = self.name
        return result.set_index(index + ['Model'])[columns]
    def get_18z(self, for_run, for_day):
        """!
        Return 18z for_day days in the future
        @param self Pointer to self
        @param for_run Which run of model to use
        @param for_day Number of days from model start to get date for
        @return Date for_days since model start
        """
        actual_date = datetime.datetime.combine(for_run.date(), datetime.time(hour=18))
        actual_date += datetime.timedelta(days=for_day - 1)
        if for_run.hour == 18:
            actual_date += datetime.timedelta(days=1)
        return actual_date
    def read_wx(self, for_run, for_date):
        """!
        Read all weather for given day
        @param self Pointer to self
        @param for_run Which run of model to use
        @param for_date Which date of model to use
        @return Weather as a pandas dataframe
        """
        def read_temp():
            return self.read_grib(for_run, for_date, 'TMP')
        def read_ugrd():
            return self.read_grib(for_run, for_date, 'UGRD')
        def read_vgrd():
            return self.read_grib(for_run, for_date, 'VGRD')
        def read_rh():
            return self.read_grib(for_run, for_date, 'RH')
        def calc_wind(x):
            """ Calculate wind indices from Series """
            return pandas.Series([common.calc_ws(x['UGRD'], x['VGRD']),
                                  common.calc_wd(x['UGRD'], x['VGRD'])],
                                 index=['WS', 'WD'])
        wx = pandas.concat([read_temp(),
                            read_rh(),
                            pandas.concat([read_ugrd(), read_vgrd()], axis=1).apply(calc_wind, axis=1)],
                           axis=1)
        # set this separately because we're overwriting the column data
        wx['TMP'] = wx[['TMP']].apply(lambda x: common.kelvin_to_celcius(x['TMP']), axis=1)
        return wx
    def get_records(self, for_run, for_day):
        """!
        Get weather for given date
        @param self Pointer to self
        @param for_run Which run of model to use
        @param for_day Which date of model to use
        @return Weather as a pandas dataframe
        """
        # need to translate for_day into an actual date
        # if for_run.hour >= 18 then does for_day == 1 mean tomorrow?
        logging.info("Loading {} records from {} run for day {}".format(self.name, for_run, for_day))
        actual_date = self.get_18z(for_run, for_day)
        rain = self.read_precip(for_run, actual_date)
        wx = self.read_wx(for_run, actual_date)
        if rain is None:
            wx['APCP'] = 0.0
        else:
            wx = wx.join(rain)
        return wx
    def read_precip_file(self, for_run, for_date):
        """!
        Read precip file for given time
        @param self Pointer to self
        @param for_run Which run of model to use
        @param for_date Which date of model to use
        @return Precipitation data as pandas dataframe
        """
        pcp = self.read_grib(for_run, for_date, 'APCP')
        # forTime = pcp.reset_index()['ForTime'][0]
        # HACK: set all negative or missing precip values to be 0
        pcp[pcp['APCP'] < 0] = 0
        pcp[pcp['APCP'] != pcp['APCP']] = 0
        return pcp
    def read_precip_interval(self, for_run, start_date, end_date):
        """!
        Calculate accumulated precip over a given period
        @param self Pointer to self
        @param for_run Which run of model to use
        @param start_date Start of interval
        @param end_date End of interval
        @return Accumulated precip over period
        """
        # we want to do end and every 6 hour interval before it up to (but not including) start
        data_end = self.read_precip_file(for_run, end_date)
        forTime = data_end.reset_index()['ForTime'][0]
        data_period = data_end
        for_date = end_date + datetime.timedelta(hours=-6)
        while for_date > start_date:
            data = self.read_precip_file(for_run, for_date)
            old_columns = data.columns
            data = data.reset_index()
            all_columns = data.columns
            old_index = [x for x in all_columns if x not in old_columns]
            data['ForTime'] = forTime
            # HACK: want to keep this as 18z time for it all
            data = data.set_index(old_index)
            data_period = data_period + data
            for_date += datetime.timedelta(hours=-6)
        return data_period
    def read_precip(self, for_run, actual_date):
        """!
        Read accumulated precip for given date
        @param self Pointer to self
        @param for_run Which run of model to use
        @param actual_date Date that actuals are for
        @return Accumulated precipitation for 24-hour period on date
        """
        # no rain at 000
        # :APCP:surface:0-3 hour acc fcst:      -- generalized precip
        # :ACPCP:surface:0-3 hour acc fcst:     -- convective precip
        # 18z is used for 1300
        # need to calculate 18z - 12z to get rain since 0800
        # and then we add 0800 obs rain to get rain between 1300 yesterday and today
        # everything after day 1 is just 18z - 18z yesterday
        if for_run.date() == actual_date.date():
            pcp = None
            if for_run.hour - 12 > 0:
                date_12z = datetime.combine(actual_date.date(), datetime.time(hour=12))
                pcp = self.read_precip_interval(for_run, date_12z, actual_date)
            # need to add in 0800 observed
            return pcp
        else:
            yesterday = actual_date + datetime.timedelta(days=-1)
            return self.read_precip_interval(for_run, yesterday, actual_date)
    def get_nearest_run(self, interval):
        """!
        Find time of most recent run with given update interval
        @param self Pointer to self
        @param interval How often model is run (hours)
        @return datetime for closest model run to current time
        """
        now = datetime.datetime.now()
        nearest_run = int(interval * round(now.hour / interval))
        return datetime.datetime.combine(now.date(), datetime.time(nearest_run))
    def load_past_records(self, year=None, force=False):
        """!
        Determine which past run files we have and load them
        @param self Pointer to self
        @param year Year to load files for, or None to load all years
        @param force Whether or not to force loading if records already exist
        @return None
        """
        import glob
        files = glob.glob(self.DIR_DATA + '/{}_*_TMP*'.format(self.name))
        def file_run(file):
            start = file.index('_') + 1
            end = file.index('_', start)
            return file[start:end]
        runs = list(set([file_run(d) for d in files]))
        # sort so we do the dates chronologically
        runs.sort()
        for run in runs:
            for_run = datetime.datetime.strptime(run, '%Y%m%d%H')
            try:
                if not year or for_run.year == year:
                    self.load_specific_records(for_run, force)
            except:
                logging.error("Unable to load run for {}".format(for_run))
    def load_specific_records(self, for_run, force=False):
        """!
        Load records for specific period
        @param self Pointer to self
        @param for_run Which run of model to use
        @param force Whether or not to force loading if records already exist
        @return Timestamp of run that records were loaded for
        """
        # save into database that corresponds to the start of this run
        # want to put the data into the database for the start date but check if it exists based on for_run
        start_date = for_run + datetime.timedelta(hours=self.lead_time)
        dbname = common.get_database(start_date)
        # if at any point for_run is already in the database then we're done
        if not force:
            logging.debug('Checking if data is already present for {} model generated at {}'.format(self.name, for_run))
            exists = self.check_exists(for_run, dbname)
            if exists:
                logging.debug('Data already loaded - aborting')
                return pandas.Timestamp(for_run)
        results = []
        for d in self.for_days:
            results.append(self.get_records(for_run, d))
        # don't save data until everything is loaded
        wx = pandas.concat(results)
        self.save_data(wx, dbname)
        # return the run that we ended up loading data for
        # HACK: Timestamp format is nicer than datetime's
        return pandas.Timestamp(for_run)
    def load_records(self, max_retries=5, force=False):
        """!
        Load the latest records using the specified interval to determine run
        @param self Pointer to self
        @param max_retries Maximum number of retries before failure
        @param force Whether or not ot force loading if records already exist
        @return None
        """
        common.check_proxy()
        for_run = self.get_nearest_run(self.interval)
        for i in xrange(max_retries):
            try:
                return self.load_specific_records(for_run)
            except urllib2.HTTPError as ex:
                logging.error(ex)
                # HACK: we set the URL in the place the error originated from
                logging.error(ex.url)
                if i + 1 == max_retries:
                    logging.critical("Too many failures - unable to retrieve data")
                    raise
                for_run = for_run + datetime.timedelta(hours=-self.interval)
                logging.error("**** Moving back 1 run since data is unavailable. Now looking for {}".format(for_run.strftime("%Y%m%d%H")))
    def __init__(self, name, for_days, interval, script, mask, dir, no_download=False, lead_time=6):
        """!
        Instantiate class
        @param name Name for weather being loaded
        @param for_days Which days to load for
        @param interval how often this data gets updated (hours)
        @param script Script in URL to query from
        @param mask Mask to use for making URL to download
        @param dir Subdirectory to download files from
        @param no_download Whether or not to not download files
        @param lead_time number of hours run happens before start date within run
        """
        super(GribLoader, self).__init__(name, for_days, no_download)
        ## number of hours run happens before start date within run
        self.lead_time = lead_time
        ## how often this data gets updated (hours)
        self.interval = interval
        ## URL root to download from
        self.host = common.CONFIG.get('FireGUARD', 'naefs_server')
        ## Script in URL to query from
        self.script = script
        ## Mask to use for making URL to download
        self.mask = mask
        ## Subdirectory to download files from
        self.dir = dir
