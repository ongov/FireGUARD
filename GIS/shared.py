"""Utility code"""

print "Importing packages..."
import sys
sys.path.append('..\util')
import common
import pandas as pd
import arcpy
import arcinfo
from arcpy.sa import *
import os
import re
import math
import time

# HACK: import this so that we don't get error on sys.stdout.flush()
import sys
from sys import stdout

print "Checking out extensions..."
arcpy.CheckOutExtension("spatial")

## Default setting for raster pyramid creation
arcpy.env.pyramid = "PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP"
## MNR Lambert Conformal Conic projection
MNR_LAMBERT = arcpy.SpatialReference('Projected Coordinate Systems/National Grids/Canada/NAD 1983 CSRS Ontario MNR Lambert')
## Default projection to use
PROJECTION = MNR_LAMBERT
## Stack of environments that have been pushed
ENVIRONMENTS = []

def env_push():
    """Push all environment variables so we can revert easily"""
    env = {}
    for key in arcpy.env:
        env[key] = arcpy.env[key]
    ENVIRONMENTS.append(env)


def env_clear():
    """Revert to original settings for all environment variables"""
    # no error check so that we know if we did things wrong
    env = ENVIRONMENTS[0]
    for key in env:
        try:
            arcpy.env[key] = env[key]
        except:
            # must be a read-only property, so no way we changed it and don't need to revert
            pass


def env_pop():
    """Revert to last settings for all environment variables"""
    # no error check so that we know if we did things wrong
    env = ENVIRONMENTS.pop()
    for key in env:
        try:
            arcpy.env[key] = env[key]
        except:
            # must be a read-only property, so no way we changed it and don't need to revert
            pass

def setSnapAndExtent(feature):
    """Set snapRaster and extent to match feature"""
    arcpy.env.snapRaster = feature
    arcpy.env.extent = feature

def isNotNoneOrInvalid(feat):
    """Check if feature class is not valid"""
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
    """Set default settings for environment"""
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

def checkGDB(folder, name=None):
    """Check if GDB exists and make it if not"""
    if not name:
        name = os.path.basename(folder)
        folder = os.path.dirname(folder)
    gdb = os.path.join(folder, name)
    if not gdb.endswith('.gdb'):
        gdb += '.gdb'
    print "Checking for " + gdb
    # HACK: for some reason Exists is crashing when the gdb directory isn't there?
    if (not os.path.isdir(gdb)):
        print "Creating " + gdb
        try:
            arcpy.CreateFileGDB_management(folder, name)
        except:
            if not arcpy.Exists(gdb):
                # if it exists then maybe another process made it in the meantime
                raise
    return gdb

def check_make(result, fct, force=False):
    """Check if an output exists and make it with the given function if not"""
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

def project_raster(in_raster, out_raster, cellsize_m="", resampling_type="", projection=PROJECTION):
    """Project a raster into the default coordinate system with the proper cell size and reference point"""
    cell_size = "{} {}".format(cellsize_m, cellsize_m) if cellsize_m else ""
    geographic_transform = find_transformation(arcpy.Describe(in_raster).spatialReference, projection)
    arcpy.ProjectRaster_management(in_raster, out_raster, projection, resampling_type, cell_size, geographic_transform, "0 0", "")

def project(in_feature, out_feature, projection=PROJECTION):
    """Project feature if output doesn't exist already"""
    def do_project(_):
        arcpy.Project_management(in_feature, _, projection, "", "", "PRESERVE_SHAPE")
        print "Repairing geometry..."
        arcpy.RepairGeometry_management(_)
    return check_make(out_feature, do_project)

def clip_raster_box(in_raster, clip_feature, out_raster):
    """Clip raster to a feature"""
    in_proj = arcpy.Describe(in_raster).spatialReference
    clip_proj = arcpy.Describe(clip_feature).spatialReference
    tmp = None
    clip_with = clip_feature
    if in_proj.exporttostring() != clip_proj.exporttostring():
        tmp = project(clip_with, arcpy.CreateScratchName(), projection=arcpy.Describe(in_raster).spatialReference)
        # project the clipping features to the input features projection so clip works
        clip_with = tmp
    env_push()
    env_defaults(mask="", extent="", cellSize=in_raster)
    oldSpatial = arcpy.env.outputCoordinateSystem
    arcpy.env.outputCoordinateSystem = arcpy.Describe(in_raster).spatialReference
    clipBuffer = calc("ClipBuffer", lambda _: arcpy.PolygonToRaster_conversion(clip_with, arcpy.ListFields(clip_with)[0].name, _))
    #~ clipBuffer = calc("ClipBuffer", lambda _: CreateConstantRaster(0, extent=clip_with))
    out_raster = calc(out_raster, lambda _: Con(IsNull(clipBuffer), clipBuffer, in_raster))
    arcpy.Delete_management(clipBuffer)
    arcpy.env.outputCoordinateSystem = oldSpatial
    env_pop()
    if tmp:
        # assuming this is simple enough that deleting every time makes sense
        arcpy.Delete_management(tmp)
    return out_raster

def raster_path(raster):
    """Get path for raster"""
    return os.path.join(raster.path, raster.name) if type(raster) == Raster else raster

def find_transformation(spatialReference, projectedReference):
    """Figure out a valid transformation from the spatialReference to the desired one"""
    try:
        # don't use extent because this gives the same first option as picking in Project Raster tool
        list = arcpy.ListTransformations(spatialReference, projectedReference)
        # if no transformations then assum that this means no transformation required
        return list[0] if len(list) > 0 else ""
    except:
        # HACK: assume no transformation if we can't find one
        return ""

def calc(save_to, fct, retries=5, buildPyramids=True, force=False):
    """Create raster from function if it does not exist already"""
    def do_calc(_):
        r = fct(_)
        if r is not None and 'save' in dir(r):
            # do this so we can also use functions that don't return a raster
            r.save(_)
        del r
        if buildPyramids:
            has_pyramids = False
            #~ # HACK: really not working for some reason
            #~ retry = 0
            #~ while retry < retries and not has_pyramids:
            try:
                print "Building pyramids"
                arcpy.BuildPyramids_management(_)
                has_pyramids = True
            except:
                #~ retry += 1
                #~ delay = math.pow(2, retry)
                #~ print "Building pyramids failed.  Retrying in {} seconds...".format(delay)
                print "Building pyramids failed."
                #~ time.sleep(delay)
        return _
    return Raster(check_make(save_to, do_calc, force))

def calc_mask(save_to, input):
    """Create a mask of where a raster has values"""
    return calc(save_to, lambda _: Int((input if type(input) == Raster else Raster(input)) * 0))

def clearData(feat, result):
    """Make a copy of a feature with not data columns"""
    info = arcpy.FieldInfo()
    fields = arcpy.ListFields(feat)
    for field in fields:
        if field.name not in ['OBJECTID']:
            info.addField(field.name, field.name, "HIDDEN", "")
    #~ arcpy.MakeFeatureLayer_management(feat, result, "", "", info)
    arcpy.MakeFeatureLayer_management(feat, "in_memory\\temp", "", "", info)
    arcpy.CopyFeatures_management("in_memory\\temp", result)
    arcpy.Delete_management("in_memory\\temp")
    return result

def getFeatures(gdb):
    """Get list of features in a workspace"""
    ws = arcpy.env.workspace
    arcpy.env.workspace = gdb
    features = map(lambda x: os.path.join(gdb, x), arcpy.ListFeatureClasses())
    arcpy.env.workspace = ws
    return features

def getRasters(gdb):
    """Get list of rasters in a workspace"""
    ws = arcpy.env.workspace
    arcpy.env.workspace = gdb
    features = map(lambda x: os.path.join(gdb, x), arcpy.ListRasters())
    arcpy.env.workspace = ws
    return features

def fixName(n):
    """Create a shortened name for raster use"""
    # have to shrink raster names to 13 characters
    n = re.sub('_w$', '', n)
    return n if len(n) <= 13 else n[:13] if '_' not in n else n[:n.index('_')] + '_' + re.sub('[a-z_]', '', n[n.index('_'):])

def try_delete(table_name):
    """Try to delete until it works"""
    if arcpy.Exists(table_name):
        try:
            arcpy.Delete_management(table_name)
        except:
            print "Delete failed for", table_name
            try_delete(table_name)


def copy_to_server(input, output=None, workspace=r'data\DSS\Fuels.gdb'):
    """Copy to ArcGIS server"""
    if not output:
        output = os.path.basename(str(input))
    print "Copying {} to server".format(str(input))
    OUT_ARCSERVER = os.path.join(r'D:\arcgisserver', workspace)
    ACTUAL_SERVER = os.path.join(r'\\' + common.CONFIG.get('FireGUARD', 'mapper_server') + r'\D$\arcgisserver', workspace)
    copied = os.path.join(OUT_ARCSERVER, output)
    if arcpy.Exists(copied):
        arcpy.Delete_management(copied)
    # remove directories if that's what we're copying
    if os.path.isdir(copied):
        os.remove(copied)
    try:
        arcpy.CopyFeatures_management(input, copied)
    except:
        try:
            arcpy.CopyRaster_management(input, copied)
        except:
            # default to basic copy if neither of those worked
            arcpy.Copy_management(input, copied)
    # copy from staging db so we're not worrying about if it was a selection or anything weird
    on_server = os.path.join(ACTUAL_SERVER, output)
    if arcpy.Exists(on_server):
        arcpy.Delete_management(on_server)
    # remove directories if that's what we're copying
    if os.path.isdir(on_server):
        os.remove(on_server)
    arcpy.Copy_management(copied, on_server)


