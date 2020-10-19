"""Make a RamPART risk map with for a specific day"""
from __future__ import print_function

import os
import shutil
import argparse
import logging
import arcpy

from arc_util import parseExtent
from arc_util import setDataSource
from arc_util import setDayCommon
from arc_util import setText
from saveboth import saveBothMXD
from Settings import Settings
from util import find_date
from util import getMapOutput

def getRiskMXDName(i, is_actuals, run_output, fire, extent, perim):
    """!
    Get path to save risk map for given inputs to
    @param i Index of simulation date to use
    @param is_actuals Whether or not simulation was run for actual weather
    @param run_output Folder simulation output was saved to
    @param fire Fire simulation was for
    @param extent Extent to use for map
    @param perim Perimeter to display on map
    @return Path to use for saving output with given inputs
    """
    prefix = 'actuals_' if is_actuals else 'wxshield_'
    fire_prefix = fire + "_" + ('actual_' if is_actuals else '')
    probs = [x for x in os.listdir(os.path.join(Settings.HOME_DIR, run_output)) if x.startswith(prefix) and x[-3:] == "asc"]
    map_output = getMapOutput(run_output)
    dates = map(find_date, probs)
    return os.path.join(map_output, fire_prefix + dates[i] + "_risk.mxd")

def getRiskMXD(i, is_actuals, run_output, fire, extent, perim, score):
    """!
    Save risk map for given inputs
    @param i Index of simulation date to use
    @param is_actuals Whether or not simulation was run for actual weather
    @param run_output Folder simulation output was saved to
    @param fire Fire simulation was for
    @param extent Extent to use for map
    @param perim Perimeter to display on map
    @param score Score for given day
    @return Path used for saving output with given inputs
    @return MapDocument with opened output
    @return extent Extent that was applied to the map
    """
    logging.debug("Running getRiskMXD() for {}".format(i))
    prefix = 'actuals_' if is_actuals else 'wxshield_'
    map_output = getMapOutput(run_output)
    copyMXD = getRiskMXDName(i, is_actuals, run_output, fire, extent, perim)
    shutil.copyfile(os.path.join(Settings.HOME_DIR, "mxds", "rampart.mxd"), copyMXD)
    theMXD = arcpy.mapping.MapDocument(copyMXD)
    extent, prob = setDayCommon(i,
                                is_actuals,
                                theMXD,
                                run_output,
                                fire,
                                perim,
                                extent)
    prob_input = os.path.join(run_output, prob)
    total_path = os.path.join(map_output, prob_input.replace(prefix, 'RA_').replace('.asc', '.tif'))
    setDataSource(theMXD, "*Relative Risk*", total_path)
    setText(theMXD, "txtScore", score)
    arcpy.RefreshActiveView()
    theMXD.save()
    return copyMXD, theMXD, extent


def saveRiskMXD(i, is_actuals, run_output, fire, extent, perim, score):
    """!
    Save risk map for given inputs
    @param i Index of simulation date to use
    @param is_actuals Whether or not simulation was run for actual weather
    @param run_output Folder simulation output was saved to
    @param fire Fire simulation was for
    @param extent Extent to use for map
    @param perim Perimeter to display on map
    @param score Score for given day
    @return None
    """
    copyMXD, theMXD, extent = getRiskMXD(i, is_actuals, run_output, fire, extent, perim, score)
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
    parser.add_argument("score", help="calculated risk score")
    parser.add_argument("--actuals", action="store_true", help="is for actuals")
    parser.add_argument("--perim", help="perimeter to show on map")
    args = parser.parse_args()
    extent = parseExtent(args.extent)
    saveRiskMXD(int(args.i), args.actuals, args.run_output, args.fire, extent, args.perim, args.score)


if __name__ == "__main__":
    doRun()
