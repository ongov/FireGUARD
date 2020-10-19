"""Make FBP fuels map"""
from __future__ import print_function

import os
import shutil
import argparse
import logging
import arcpy

from arc_util import findFuelRaster
from arc_util import parseExtent
from arc_util import setCommon
from arc_util import setDataSource
from saveboth import saveBothMXD
from Settings import Settings
from util import find_lines
from util import getMapOutput
from util import readSimOutput

def getFuelMXDName(fire_prefix, run_output, fire, extent, perim):
    """!
    Get path to save fuel map for given inputs to
    @param fire_prefix prefix to use for file name
    @param run_output Folder simulation output was saved to
    @param fire Fire simulation was for
    @param extent Extent to use for map
    @param perim Perimeter to display on map
    @return Path to use for saving output with given inputs
    """
    map_output = getMapOutput(run_output)
    return os.path.join(map_output, fire_prefix + "_fuels.mxd")

def getFuelMXD(fire_prefix, run_output, fire, extent, perim):
    """!
    Save fuel map for given inputs
    @param fire_prefix prefix to use for file name
    @param run_output Folder simulation output was saved to
    @param fire Fire simulation was for
    @param extent Extent to use for map
    @param perim Perimeter to display on map
    @return Path used for saving output with given inputs
    @return MapDocument with opened output
    @return extent Extent that was applied to the map
    """
    logging.debug("Called getFuelMXD()")
    sim_output = readSimOutput(run_output)
    copyMXD = getFuelMXDName(fire_prefix, run_output, fire, extent, perim)
    shutil.copyfile(os.path.join(Settings.HOME_DIR, "mxds", "fuels.mxd"), copyMXD)
    theMXD = arcpy.mapping.MapDocument(copyMXD)
    txtAssumptions = ("FBP Fuels are derived from eFRI data and the CFS national fuel grid.\n" +
                        "Features under 1ha in size may not be accurately reflected.\n" +
                        "Fuels substituted in the following manner:\n" +
                        '\n'.join(find_lines(sim_output, 'is treated like', 'Fuel')))
    fbp = setDataSource(theMXD, "*FBP*", findFuelRaster(sim_output))
    setCommon(theMXD,
              fire,
              txtAssumptions,
              " ",
              run_output,
              fire,
              perim,
              extent,
              fbp)
    arcpy.RefreshActiveView()
    theMXD.save()
    return copyMXD, theMXD

def saveFuelMXD(fire_prefix, run_output, fire, extent, perim):
    """!
    Save fuel map for given inputs
    @param fire_prefix prefix to use for file name
    @param run_output Folder simulation output was saved to
    @param fire Fire simulation was for
    @param extent Extent to use for map
    @param perim Perimeter to display on map
    @return None
    """
    copyMXD, theMXD = getFuelMXD(fire_prefix, run_output, fire, extent, perim)
    saveBothMXD(copyMXD, theMXD, copyMXD.replace('.mxd', '.png'))
    del theMXD

def doRun():
    """!
    Run with command line arguments
    @return None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("fire_prefix", help="prefix to use for naming")
    parser.add_argument("run_output", help="folder that outputs are in")
    parser.add_argument("fire", help="fire that this is for")
    parser.add_argument("extent", help="extent to center map on")
    parser.add_argument("--perim", help="perimeter to show on map")
    args = parser.parse_args()
    extent = parseExtent(args.extent)
    saveFuelMXD(args.fire_prefix, args.run_output, args.fire, extent, args.perim)

if __name__ == "__main__":
    doRun()