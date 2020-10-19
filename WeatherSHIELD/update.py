"""Run all scripts to update current data"""

import logging
import sys
sys.path.append('..\util')
import common
from fpaloader import FPALoader
from gefsloader import GefsLoader
from gepsloader import GepsLoader
import dfoss
import gethistoric
import sst

def try_no_fail(fct):
    """!
    Try to run function and ignore failure
    @param fct Function to run
    @return None
    """
    try:
        fct()
    except KeyboardInterrupt as ke:
        logging.debug('Aborting due to user cancel')
        raise ke
    except Exception as e:
        logging.debug('Call failed but ignoring error')

def get_standard():
    """!
    Get standard available weather
    @return None
    """
    try_no_fail(dfoss.load)
    try_no_fail(gethistoric.get_standard)
    try_no_fail(FPALoader().load_records)
    try_no_fail(GefsLoader().load_records)
    try_no_fail(GepsLoader().load_records)
    try_no_fail(sst.load)


# run get_standard() for each file
if __name__ == "__main__":
    get_standard()
