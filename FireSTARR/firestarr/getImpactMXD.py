"""Make Total Potential Impact map"""
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
from util import findSuffix
from util import getMapOutput
from util import readSimOutput

def getImpactMXDName(fire_prefix, run_output, fire, extent, perim):
    """!
    Get path to save impact map for given inputs to
    @param fire_prefix prefix to use for file name
    @param run_output Folder simulation output was saved to
    @param fire Fire simulation was for
    @param extent Extent to use for map
    @param perim Perimeter to display on map
    @return Path to use for saving output with given inputs
    """
    map_output = getMapOutput(run_output)
    return os.path.join(map_output, fire_prefix + "_impact.mxd")

def getImpactMXD(fire_prefix, run_output, fire, extent, perim):
    """!
    Save impact map for given inputs
    @param fire_prefix prefix to use for file name
    @param run_output Folder simulation output was saved to
    @param fire Fire simulation was for
    @param extent Extent to use for map
    @param perim Perimeter to display on map
    @return Path used for saving output with given inputs
    @return MapDocument with opened output
    @return extent Extent that was applied to the map
    """
    logging.debug("Called getImpactMXD()")
    sim_output = readSimOutput(run_output)
    map_output = getMapOutput(run_output)
    copyMXD = getImpactMXDName(fire_prefix, run_output, fire, extent, perim)
    shutil.copyfile(os.path.join(Settings.HOME_DIR, "mxds", "impact.mxd"), copyMXD)
    theMXD = arcpy.mapping.MapDocument(copyMXD)
    impact =Settings.RAMPART_MASK.format('high', findSuffix(findFuelRaster(sim_output)))
    setDataSource(theMXD, "*Potential Impact*", impact)
    txtAssumptions = ("Potential Impact is based on staff assessment of impact on a 1 - 10 scale,\n"
                       "representing the loss from the damage or disruption from various types of RA data\n"
                       "burned with a 4000+ kW/m head fire intensity. Each cell is coloured based on the\n"
                       "amount and type of RA within it. Potential Impact is the 'worst case'\n"
                       "and the risk calculation on subsequent maps is a downscaling of this (e.g., burned\n"
                       "with lower fire intensity and/or lower probability). Warning: use with caution and\n"
                       "awareness of the assumptions and simplifications. Impact does not include indirect\n"
                       "(e.g. smoke) or long-term effects. A hectare must burn in the model to show any risk;\n"
                       "limitations of FireSTARR apply. RA may be missing from the GIS database, affecting\n"
                       "results.")
    setCommon(theMXD,
              fire,
              txtAssumptions,
              " ",
              run_output,
              fire,
              perim,
              extent,
              impact)
    arcpy.RefreshActiveView()
    theMXD.save()
    return copyMXD, theMXD

def saveImpactMXD(fire_prefix, run_output, fire, extent, perim):
    """!
    Save impact map for given inputs
    @param fire_prefix prefix to use for file name
    @param run_output Folder simulation output was saved to
    @param fire Fire simulation was for
    @param extent Extent to use for map
    @param perim Perimeter to display on map
    @return None
    """
    copyMXD, theMXD = getImpactMXD(fire_prefix, run_output, fire, extent, perim)
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
    saveImpactMXD(args.fire_prefix, args.run_output, args.fire, extent, args.perim)


if __name__ == "__main__":
    doRun()
