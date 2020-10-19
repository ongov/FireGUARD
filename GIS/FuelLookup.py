"""Code for lookup for FBP fuels derived from a .lut file like prometheus uses"""

import arcpy
import arcinfo
from arcpy.sa import *
import shared
from shared import *

class FuelLookup:
    """Fuel lookup based on .lut file"""
    def __init__(self, filename):
        """Initialize from .lut file"""
        fuels = pd.read_csv(filename)
        fuels.columns = map(lambda x: x.strip(), fuels.columns)
        # requires pandas >= 0.17
        fuel_dict = fuels[['grid_value', 'fuel_type']].set_index('grid_value').to_dict('index')
        ## Dictionary of values by fuel name
        self.by_fuel = {}
        ## Dictionary of fuel names by value
        self.by_value = {}
        for k in fuel_dict.keys():
            # HACK: unkey these and shorten them
            v = fuel_dict[k]['fuel_type']
            # keep everything before the first space
            if ' ' in v:
                v = v[:v.index(' ')]
            fuel_dict[k] = v
            int_k = int(k)
            if v not in self.by_fuel:
                self.by_fuel[v] = set([int_k])
            else:
                self.by_fuel[v] = set(list(self.by_fuel[v]) + [int_k])
            self.by_value[int_k] = v
        self.by_value[-9999] = 'Unknown'
        self.by_value[None] = 'Unknown'
        # FIX: need to use D-1 and O-1 so mapper is okay
        #
        ## list of fuels considered M3/M4
        self.m3m4 = ['M-3', 'M-4', 'M-3/M-4']
        ## list of fuels considered conifer
        self.conifer = sorted([x for x in self.by_fuel.keys() if 'C' == x[0]])
        ## list of fuels considered deciduous
        self.deciduous = sorted([x for x in self.by_fuel.keys() if 'D' == x[0]])
        ## list of fuels considered mixedwood
        self.mixedwood = sorted([x for x in self.by_fuel.keys() if 'M' == x[0]])
        ## list of all fuels not in one of previous categories
        self.other = sorted([x for x in self.by_fuel.keys() if x not in self.conifer and x not in self.deciduous and x not in self.mixedwood])
        ## Sorted list of fuel names
        self.all_keys = sorted(self.by_fuel.keys())
        ## Sorted list of values
        self.all_values = sorted(self.findValues(self.all_keys))
        ## list of all fuels that are not m3/m4
        self.nonm3m4 = self.findValues(sorted([x for x in self.all_keys if x not in self.m3m4]))
        ## used to map fuels to the number to use if no percentage specified
        self.repl = {}
        for v in sorted(self.by_fuel.keys()):
            if 1 < len(self.by_fuel[v]):
                # replace all instances of the value with the lowest value
                self.repl[min(self.by_fuel[v])] = [x for x in sorted(self.by_fuel[v]) if x != min(self.by_fuel[v])]
        for k, vals in self.repl.iteritems():
            for v in vals:
                if k != (10 * int(v / 100)) and v >= 200:
                    print("Invalid value: {} {}".format(k, v))
    def findValues(self, keys):
        """Find values for given keys"""
        values = []
        for k in keys:
            values += self.by_fuel[k]
        return values
    def setListNull(self, input, output, null_list):
        """Set everything that matches the list to be null in the raster"""
        result = SetNull(InList(input, null_list), input)
        result.save(output)
    def byKeys(self, input, output, keys):
        """Save raster with only values of given keys"""
        values = self.findValues(keys)
        result = InList(input, values)
        result.save(output)
    def byKeysRev(self, input, output, keys):
        """Save raster with only values not in given keys"""
        values = self.findValues(keys)
        result = SetNull(InList(input, values), input)
        result.save(output)
    def makeRaster(self, src, dest, keys):
        """Make raster from source by selecting based on keys"""
        return calc(dest, lambda _: self.byKeys(src, dest, keys))
    def makeM3M4(self, src, dest):
        """Make raster of M3/M4 values"""
        return self.makeRaster(src, dest, self.m3m4)
    def makeConifer(self, src, dest):
        """Make raster of conifer values"""
        return self.makeRaster(src, dest, self.conifer)
    def makeDeciduous(self, src, dest):
        """Make raster of deciduous values"""
        return self.makeRaster(src, dest, self.deciduous)
    def makeMixedwood(self, src, dest):
        """Make raster of mixedwood values"""
        return self.makeRaster(src, dest, self.mixedwood)
