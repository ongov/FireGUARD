"""Load GEFS data"""

from gribloader import GribLoader


class GefsLoader(GribLoader):
    """ Loads GEFS data """
    def __init__(self, no_download=False):
        """!
        Instantiate class
        @param no_download Whether or not to not download if data already exists
        """
        name = 'GEFS'
        ## Script in URL to query from  
        script = r'filter_gefs_atmos_0p50a.pl'
        ## Mask to use for making URL to download
        mask = r'?file={}.t{:02d}z.pgrb2a.0p50.f{:03d}'
        ## Subdirectory to download files from
        dir = r'&dir=%2Fgefs.{}%2F{}%2Fatmos%2Fpgrb2ap5'
        super(GefsLoader, self).__init__(name=name,
                                         for_days=range(1, 16),
                                         interval=6,
                                         script=script,
                                         mask=mask,
                                         dir=dir,
                                         num_members=31,
                                         no_download=no_download)


if __name__ == "__main__":
    GefsLoader().load_records()
