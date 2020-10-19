"""Shared functions that use arcpy"""
print "Importing packages..."
import os
import re
import math
import time

import arcpy

# HACK: import this so that we don't get error on sys.stdout.flush()
import sys
from sys import stdout

## Stack of environment settings that have been pushed
ENVIRONMENTS = []

def env_push():
    """!
    Push all environment variables so we can revert easily
    @return None
    """
    import arcpy
    env = {}
    for key in arcpy.env:
        env[key] = arcpy.env[key]
    ENVIRONMENTS.append(env)

def env_pop():
    """!
    Revert to last settings for all environment variables
    @return None
    """
    import arcpy
    # no error check so that we know if we did things wrong
    env = ENVIRONMENTS.pop()
    for key in env:
        try:
            arcpy.env[key] = env[key]
        except:
            # must be a read-only property, so no way we changed it and don't need to revert
            pass

def setSnapAndExtent(feature):
    """!
    Set snapRaster and extent to match feature
    @param feature Raster to use for snapping and extent
    @return None
    """
    import arcpy
    arcpy.env.snapRaster = feature
    arcpy.env.extent = feature

def isNotNoneOrInvalid(feat):
    """!
    Check if feature exists and is valid
    @param feat feature class path to check for
    @return Whether or not feature exists
    """
    import arcpy
    return feat is not None and ((type(feat) == str and feat == "") or arcpy.Exists(feat))

def env_defaults(
            snapAndExtent=None,
            pyramid="PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP",
            overwriteOutput=1,
            addOutputsToMap=False,
            workspace=None,
            mask=None,
            cellSize=None,
            snapRaster=None,
            extent=None
    ):
    """!
    Set default settings for environment
    @param snapAndExtent Raster to set snap and extent to
    @param pyramid Default raster pyramid settings
    @param overwriteOutput Whether or not to overwrite outputs that already exist
    @param addOutputsToMap Whether or not to add outputs of functions to current map
    @param workspace Workspace to set as environment current
    @param mask Feature to use as environment mask
    @param cellSize Cell size to use for rasters
    @param snapRaster Raster to set snap to
    @param extent Extent for geoprocessing
    @return None
    """
    import arcpy
    arcpy.env.pyramid = pyramid
    if isNotNoneOrInvalid(snapAndExtent):
        setSnapAndExtent(snapAndExtent)
    if isNotNoneOrInvalid(snapRaster):
        arcpy.env.snapRaster = snapRaster
    if isNotNoneOrInvalid(extent):
        arcpy.env.extent = extent
    if isNotNoneOrInvalid(mask):
        arcpy.env.mask = mask
    if isNotNoneOrInvalid(cellSize):
        arcpy.env.cellSize = cellSize
    # Just overwrite all outputs instead of worrying about deleting them properly first
    arcpy.env.overwriteOutput = overwriteOutput
    # stop adding everything to the map
    arcpy.env.addOutputsToMap = addOutputsToMap
    # default to using current workspace but have parameter so we can override
    if workspace:
        arcpy.env.workspace = workspace


def check_make(result, fct, force=False):
    """!
    Check if result exists and if not make it with fct
    @param result Result to check existence of
    @param fct Function to run to make result
    @param force Whether or not to run function even if result exists
    @return Result
    """
    if result == os.path.basename(result):
        # add in workspace if not there already
        result = os.path.join(arcpy.env.workspace, result)
    if force or not arcpy.Exists(result):
        print "Creating {}".format(result)
        env_push()
        arcpy.env.overwriteOutput = True
        fct(result)
        env_pop()
    else:
        print "Already have {}".format(result)
    return result

def find_transformation(spatialReference, projectedReference):
    """!
    Figure out a valid transformation from the spatialReference to the desired one
    @param spatialReference Spatial reference to project from
    @param projectedReference Spatial reference to project to
    @return Transformation that converts the first spatial reference to the second
    """
    try:
        # don't use extent because this gives the same first option as picking in Project Raster tool
        list = arcpy.ListTransformations(spatialReference, projectedReference)
        # if no transformations then assum that this means no transformation required
        return list[0] if len(list) > 0 else ""
    except:
        # HACK: assume no transformation if we can't find one
        return ""

def project_raster(in_raster, out_raster, projection, cellsize_m="", resampling_type=""):
    """!
    Project a raster into the default coordinate system with the proper cell size and reference point
    @param in_raster Raster to project
    @param out_raster Path to save projected raster to
    @param projection Projection to apply to input raster
    @param cellsize_m Size to use for cells in projected raster (m)
    @param resampling_type Method for resampling to use
    @return None
    """
    cell_size = "{} {}".format(cellsize_m, cellsize_m) if cellsize_m else ""
    geographic_transform = find_transformation(arcpy.Describe(in_raster).spatialReference, projection)
    arcpy.ProjectRaster_management(in_raster, out_raster, projection, resampling_type, cell_size, geographic_transform, "0 0", "")

def project(in_feature, out_feature, projection):
    """!
    Project a feature to the requested projection
    @param in_feature Feature to project
    @param out_feature Path to save projected feature to
    @param projection Projection to apply
    @return Path projected feature was saved to
    """
    def do_project(_):
        """Apply the projection"""
        arcpy.Project_management(in_feature, _, projection, "", "", "PRESERVE_SHAPE")
        print "Repairing geometry..."
        arcpy.RepairGeometry_management(_)
    return check_make(out_feature, do_project)
