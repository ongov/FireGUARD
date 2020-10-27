"""Load GEPS data"""

from gribloader import GribLoader


class GepsLoader(GribLoader):
    """ Loads GEPS data """
    def __init__(self, no_download=False):
        """!
        Instantiate class
        @param no_download Whether or not to not download if data already exists
        """
        name = 'GEPS'
        ## Script in URL to query from
        script = r'filter_cmcens.pl'
        ## Mask to use for making URL to download
        mask = r'?file=cmc_{}.t{:02d}z.pgrb2a.0p50.f{:03d}'
        # mask = r'?file=cmc_gec00.t00z.pgrb2af18'
        ## Subdirectory to download files from
        dir = r'&dir=%2Fcmce.{}%2F{}%2Fpgrb2ap5'
        # r'&dir=%2Fcmce.20160419%2F00%2Fpgrb2a'
        super(GepsLoader, self).__init__(name=name,
                                         for_days=range(1, 16),
                                         interval=12,
                                         script=script,
                                         mask=mask,
                                         dir=dir,
                                         num_members=21,
                                         no_download=no_download)


if __name__ == "__main__":
    GepsLoader().load_records()
