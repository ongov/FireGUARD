"""Make a map with the FireSTARR projection for a specific day"""
from __future__ import print_function

import os
import shutil
import argparse
import logging
import arcpy

from arc_util import parseExtent
from arc_util import setDataSource
from arc_util import setDayCommon
from saveboth import saveBothMXD
from Settings import Settings
from util import find_date
from util import getMapOutput

def getProjectionMXDName(i, is_actuals, run_output, fire, extent, perim):
    """!
    Generate name of mxd to output to when using given parameters
    @param i index of date to use
    @param is_actuals Whether or not this is for actual observations
    @param run_output Folder that output is in
    @param fire Name of fire
    @param extent Extent to set on map
    @param perim Perimeter to use draw on map
    @return Name of mxd that would be output with given parameters
    """
    prefix = 'actuals_' if is_actuals else 'wxshield_'
    fire_prefix = fire + "_" + ('actual_' if is_actuals else '')
    probs = [x for x in os.listdir(os.path.join(Settings.HOME_DIR, run_output)) if x.startswith(prefix) and x[-3:] == "asc"]
    map_output = getMapOutput(run_output)
    dates = map(find_date, probs)
    return os.path.join(map_output, fire_prefix + dates[i] + ".mxd")

def getProjectionMXD(i, is_actuals, run_output, fire, extent, perim):
    """!
    Save projection maps for given inputs
    @param i index of date to use
    @param is_actuals Whether or not this is for actual observations
    @param run_output Folder that output is in
    @param fire Name of fire
    @param extent Extent to set on map
    @param perim Perimeter to use draw on map
    @return Path used for saving output with given inputs
    @return MapDocument with opened output
    @return extent Extent that was applied to the map
    """
    logging.debug("Running getProjectionMXD() for {}".format(i))
    copyMXD = getProjectionMXDName(i, is_actuals, run_output, fire, extent, perim)
    shutil.copyfile(os.path.join(Settings.HOME_DIR, "mxds", "fireguard.mxd"), copyMXD)
    theMXD = arcpy.mapping.MapDocument(copyMXD)
    extent, prob = setDayCommon(i,
                                is_actuals,
                                theMXD,
                                run_output,
                                fire,
                                perim,
                                extent)
    setDataSource(theMXD, "*Percent*", run_output, prob)
    arcpy.RefreshActiveView()
    theMXD.save()
    return copyMXD, theMXD, extent

def saveProjectionMXD(i, is_actuals, run_output, fire, extent, perim):
    """!
    Save projection maps for given inputs
    @param i index of date to use
    @param is_actuals Whether or not this is for actual observations
    @param run_output Folder that output is in
    @param fire Name of fire
    @param extent Extent to set on map
    @param perim Perimeter to use draw on map
    @return None
    """
    copyMXD, theMXD, extent = getProjectionMXD(i, is_actuals, run_output, fire, extent, perim)
    saveBothMXD(copyMXD, theMXD, copyMXD.replace('.mxd', '.png'))
    del theMXD

def doRun():
    """!
    Run with command line arguments
    @return None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("i", help="date index for map to make")
    parser.add_argument("run_output", help="folder that outputs are in")
    parser.add_argument("fire", help="fire that this is for")
    parser.add_argument("extent", help="extent to center map on")
    parser.add_argument("--actuals", action="store_true", help="is for actuals")
    parser.add_argument("--perim", help="perimeter to show on map")
    args = parser.parse_args()
    extent = parseExtent(args.extent)
    saveProjectionMXD(int(args.i), args.actuals, args.run_output, args.fire, extent, args.perim)

if __name__ == "__main__":
    doRun()
