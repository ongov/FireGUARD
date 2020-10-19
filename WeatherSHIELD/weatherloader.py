"""WeatherLoader class"""

import sys
sys.path.append('..\util')
import common
import pandas
import os

class WeatherLoader(object):
    """ Loads weather data """
    ## directory to save data
    DIR_DATA = r'data'
    ## directory to save output
    DIR_OUTPUT = r'output'
    def check_exists(self, for_run, dbname=None):
        """!
        Check if data for given Generated time already exists
        @param self Pointer to this
        @param for_run Time of run
        @param dbname Database to read from
        @return Whether or not record is already in database
        """
        cnxn = None
        try:
            cnxn = common.open_local_db(dbname)
            df = pandas.read_sql('SELECT * FROM [INPUTS].[DAT_Model] WHERE [Model]=\'{}\''.format(self.name), cnxn)
        finally:
            if cnxn:
                cnxn.close()
        return 1 == len(df.query('Generated == \'{}\''.format(for_run)))
    def save_data(self, wx, dbname=None):
        """!
        Save data into database
        @param self Pointer to this
        @param wx Weather to put into database
        @param dbname Database to write to
        @return None
        """
        common.insert_weather('INPUTS', 'DAT_Forecast', wx, database=dbname)
    def load_records(self, max_retries=5):
        """!
        Load the latest records using the specified interval to determine run
        @param self Pointer to this
        @param max_retries Maximum retries before failure
        @return None
        """
        raise NotImplementedError()
    def __init__(self, name, for_days, no_download=False):
        """!
        Constructor
        @param self Pointer to this
        @param name Name for weather being loaded
        @param for_days Which days to load for
        @param no_download Whether or not to not download files
        """   
        ## Name for weather being loaded
        self.name = name
        ## Which days to load for
        self.for_days = for_days
        common.ensure_dir(self.DIR_DATA)
        ## Folder to save downloaded weather to
        self.DIR_DATA = os.path.join(self.DIR_DATA, self.name)
        common.ensure_dir(self.DIR_DATA)
        common.ensure_dir(self.DIR_OUTPUT)
        ## Whether or not to download files
        self.no_download = no_download
