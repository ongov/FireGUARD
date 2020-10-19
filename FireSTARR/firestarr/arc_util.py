"""Helper functions that involve arcpy"""
from __future__ import print_function

import logging
import os
import arcpy

from plotsize import makeSizeGraphName
from Settings import Settings
from util import find_date
from util import find_day
from util import find_line
from util import getMapOutput
from util import getSizeAndAssumptions
from util import readSimOutput

## Possible scales to use on maps
SCALES = [25000, 50000, 100000, 250000]

def setText(theMXD, elem, text):
    """!
    Set text for element
    @param theMXD the mxd the element is in
    @param elem Element name to set text of
    @param text Text to apply to element
    @return None
    """
    try:
        arcpy.mapping.ListLayoutElements(theMXD, "", elem)[0].text = text
    except:
        # HACK: just ignore if element is missing
        pass

def setSourceImage(theMXD, elem, sourceImage):
    """!
    Set source for an image
    @param theMXD the mxd the element is in
    @param elem Element name to set path of
    @param sourceImage Path to set image to
    @return None
    """
    arcpy.mapping.ListLayoutElements(theMXD, "", elem)[0].sourceImage = sourceImage

def setDataSource(theMXD, layer, folder, source=None):
    """!
    @param theMXD the mxd the element is in
    @param layer Layer to set data source for
    @param folder folder of data source, or entire path
    @param source path within folder, or None if folder is entire path
    @return Last Layer that data source was set for
    """
    if source is None:
        source = os.path.basename(folder)
        folder = os.path.dirname(folder)
    source = source.replace(".shp", "")
    for for_layer in arcpy.mapping.ListLayers(theMXD, layer):
        for_layer.replaceDataSource(folder, "NONE", source)
    return for_layer

def parseExtent(s):
    """!
    Parse a string into an Extent
    @param s string to parse
    @return Extent that was parsed
    """
    return apply(arcpy.Extent, map(float, s.split(' ')))

def applyExtent(extent, theMXD, spatialReference):
    """!
    Apply extent to data frame in map
    @param extent Extent to apply
    @param theMXD mxd to apply to data frame of
    @param spatialReference Spatial reference of extent
    @return None
    """
    df = arcpy.mapping.ListDataFrames(theMXD, "Layers")[0]
    df.spatialReference = spatialReference
    df.extent = extent
    #set scale based on predetermined list
    s = 0
    # HACK: round so that if applying extent makes it really close then it should still work
    while s < len(SCALES) - 1 and round(df.scale / 1000.0, 0) > round(SCALES[s] / 1000.0, 0):
        s += 1
    df.scale = SCALES[s]
    df.panToExtent(extent)
    inset = arcpy.mapping.ListDataFrames(theMXD, "Inset")[0]
    inset.spatialReference = spatialReference
    inset.panToExtent(extent)

def applyPerim(perim, theMXD):
    """!
    Apply perimeter to layer within mxd
    @param perim Perimeter to apply as data source
    @param theMXD mxd to apply perimeter to
    @return string denoting perimeter used, or "" if None
    """
    final = arcpy.mapping.ListLayers(theMXD, "Actual Perimeter")[0]
    final.visible = not not perim
    if perim:
        perim_shp = os.path.basename(perim)
        perim_folder = os.path.dirname(perim).replace('\\', '/').replace('/', '\\')
        final.replaceDataSource(perim_folder, "NONE", perim_shp.replace(".shp",""))
        return '\nPerimeter ' + os.path.basename(perim)
    return ""

def setCommon(theMXD, txtDate, txtAssumptions, txtSize, run_output, fire, perim, extent, spatialReference):
    """!
    Set common elements that are on all maps
    @param theMXD mxd to apply settings to
    @param txtDate string to use for date text
    @param txtAssumptions string to use for Assumptions text
    @param txtSize string to use for size text
    @param run_output Folder that simulation outputs are in
    @param fire Fire that simulation was for
    @param perim Perimeter to show on map
    @param extent Extent to apply to map
    @param spatialReference Spatial reference for extent
    @return None
    """
    setText(theMXD, "txtOffer", Settings.ACTIVE_OFFER)
    setText(theMXD, "txtVersion", Settings.VERSION)
    setText(theMXD, "date", txtDate)
    setText(theMXD, "txtAssumptions", txtAssumptions)
    txtSize += applyPerim(perim, theMXD)
    setText(theMXD, "txtSize", txtSize)
    setDataSource(theMXD, "Origin", run_output, fire)
    applyExtent(extent, theMXD, arcpy.Describe(spatialReference).spatialReference)

def setDayCommon(i, is_actuals, theMXD, run_output, fire, perim, extent):
    """!
    Set common attributes on maps that are for a specific day
    @param i Index of date that map is for
    @param is_actuals Whether or not this is for actual weather
    @param theMXD mxd to apply settings to
    @param run_output Folder that simulation outputs are in
    @param fire Fire that simulation was for
    @param perim Perimeter to show on map
    @param extent Extent to apply to map
    @return Extent after applying to map
    @return Probability contour that was used
    """
    prefix = 'actuals_' if is_actuals else 'wxshield_'
    fire_prefix = fire + "_" + ('actual_' if is_actuals else '')
    probs = [x for x in os.listdir(os.path.join(Settings.HOME_DIR, run_output)) if x.startswith(prefix) and x[-3:] == "asc"]
    day0 =  find_day(probs[0]) - 1
    jds = map(find_day, probs)
    dates = map(find_date, probs)
    days = map(lambda x: x - day0, jds)
    sim_output = readSimOutput(run_output)
    txtSize, txtAssumptions = getSizeAndAssumptions(i, sim_output, days, dates)
    map_output = getMapOutput(run_output)
    f = os.path.join(run_output, probs[i].replace(prefix, 'sizes_').replace('.asc', '.csv'))
    size_graph = makeSizeGraphName(f)
    setSourceImage(theMXD, "graph_stats", size_graph)
    prob_source = os.path.join(map_output, probs[i].replace(".asc", "_class_poly.shp").replace("-", "_"))
    low_prob = setDataSource(theMXD, "Low Probability", prob_source)
    gtr10 = setDataSource(theMXD, "> 10%", prob_source)
    df = arcpy.mapping.ListDataFrames(theMXD, "Layers")[0]
    df.spatialReference = arcpy.Describe(prob_source).spatialReference
    if not extent:
        # only set extent based on final map so that they all cover the same area
        #~ extent = gtr10.getSelectedExtent()
        extent = low_prob.getSelectedExtent()
        # HACK: do this here so the same extent gets applied to subsequent maps
        applyExtent(extent, theMXD, df.spatialReference)
        extent = df.extent
    setCommon(theMXD,
              fire + "\n" + dates[i] + ' - Day ' + str(days[i]),
              txtAssumptions,
              txtSize,
              run_output,
              fire,
              perim,
              extent,
              prob_source)
    return df.extent, probs[i]

def findFuelRaster(sim_output):
    """!
    Find fuel raster from simulation output
    @param sim_output Simulation output folder
    @return Path to fuel raster that was used
    """
    result = find_line(sim_output, 'Fuel raster is ', 'Fuel raster is ')
    if result.startswith('..'):
        result = os.path.abspath(os.path.join(Settings.HOME_DIR, result))
    return result
