"""Load previous records that aren't in database"""

import sys

if __name__ == "__main__":
    ## year to load for
    year = None
    if len(sys.argv) > 1 and sys.argv[1] not in ['dfoss', 'fpa', 'historic', 'geps', 'gefs']:
        year = int(sys.argv[1])
        print "Loading year {}".format(year)
    if len(sys.argv) == 1 or 'dfoss' in sys.argv:
        # this is really overkill usually since it only needs to happen once
        if year is None:
            import dfoss
            dfoss.load_past_records()
    if len(sys.argv) == 1 or 'fpa' in sys.argv:
        import fpaloader
        ## FPALoader to use for loading
        loader = fpaloader.FPALoader(True)
        loader.load_past_records(year)
        loader.load_dumped_records(year)
    if len(sys.argv) == 1 or 'historic' in sys.argv:
        import gethistoric
        gethistoric.load_past_records(year)
    if len(sys.argv) == 1 or 'geps' in sys.argv:
        import gepsloader
        loader = gepsloader.GepsLoader(True)
        loader.load_past_records(year)
    if len(sys.argv) == 1 or 'gefs' in sys.argv:
        import gefsloader
        loader = gefsloader.GefsLoader(True)
        loader.load_past_records(year)
