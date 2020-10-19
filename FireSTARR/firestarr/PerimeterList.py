"""PerimeterList class"""
from __future__ import print_function

import fnmatch
import os

from dateutil.parser import parse

from log import *

from util import parse_date

class PerimeterList:
    """Loads perimeters for fire matching the given year and mask"""
    def __init__(self, year, fire_mask):
        """!
        Find files that match the given criteria
        @param self Pointer to this
        @param year Year to find perimeters for
        @param fire_mask Mask to find matching perimeters for
        """
        from Settings import Settings
        ## Year to load for
        self.year = year
        ## Dictionary of perimeters by specific fire
        self.by_fire = {}
        ## List of all perimeters that match fire mask
        self.all_shps = []
        logging.debug("Finding perimeters...")
        perim_root = Settings.PERIM_ROOT
        if year < 2020:
            perim_root = Settings.PERIM_ARCHIVE_ROOT.format(year)
        if os.path.exists(perim_root):
            for d in os.listdir(perim_root):
                if not fire_mask or fire_mask in d:
                    for root, dirs, files in os.walk(os.path.join(perim_root, d)):
                        for file in fnmatch.filter(files, "*.shp"):
                            f = file.upper()
                            if "_I_" in f or "_F_" in f or "_I.SHP" in f or "_F.SHP" in f or "_PROG_" in f:
                                # HACK: poorly named files are causing issues
                                if ".SHP.SHP" not in f and "_ICS_" not in f and "LINE" not in f and "PROJECTIONS" not in f:
                                    self.all_shps += [os.path.join(root, file)]
            logging.debug("Done finding perimeters...")
        else:
            logging.error("No access to perimeter directory {}".format(perim_root))
    def get_perims(self, fire):
        """!
        Return perimeters that match a specific fire
        @param self Pointer to this
        @param fire Fire to find perimeters for
        @return Dictionary of dates to perimeters
        """
        if not self.by_fire.has_key(fire):
            shps = {'by_date': {}}
            max_date = None
            by_date = shps['by_date']
            for s in self.all_shps:
                if fire in s:
                    if "_F_" in s:
                        shps['Final'] = s
                    cur_date = parse_date(s, self.year)
                    # HACK: import here to avoid dependency loop
                    from gis import GetFeatureCount
                    # don't use if there aren't any features in the file
                    if cur_date and 0 < GetFeatureCount(s):
                        by_date[cur_date] = s
                        if not max_date or cur_date > max_date:
                            max_date = cur_date
            if 0 == len(by_date):
                shps = None
            elif not shps.has_key('Final'):
                shps['Final'] = by_date[max_date]
            self.by_fire[fire] = shps
        return self.by_fire[fire]
    def find_perim(self, fire, day):
        """!
        Return perimter for a specific fire on a specific day
        @param self Pointer to this
        @param fire Fire to find perimeter for
        @param day Date to find perimeter for
        @return Perimeter that is on or last before given date
        """
        shps = self.get_perims(fire)
        if not shps:
            # no perimeters exist
            return ''
        if 'Final' == day:
            return shps['Final']
        # find the last day less than or equal to the day we want
        for_day = parse(day)
        possible = [x for x in shps['by_date'].keys() if x <= for_day]
        if 0 == len(possible):
            return ''
        return shps['by_date'][max(possible)]
