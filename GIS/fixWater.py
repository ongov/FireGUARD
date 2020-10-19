"""Create FBP fuel rasters from eFRI data and other inputs"""
from __future__ import print_function

# NOTE: seems to need to be run in ArcMap for:
# - the USA water
# - the mapper creation

import sys
sys.path.append('..\util')
import common

CELLSIZE_M = 100
import pandas as pd

# HACK: import this so that we don't get error on sys.stdout.flush()
import sys
from sys import stdout
import os

#~ HOME_DIR = os.path.dirname(os.path.realpath(__import__("__main__").__file__))
HOME_DIR = "C:\\FireGUARD\\GIS"
sys.path.append(HOME_DIR)
sys.path.append(os.path.join(HOME_DIR, 'fbp_convert'))
import shared
#~ reload(shared)
from shared import *
import fuelconversion
#~ reload(fuelconversion)
from util import ensure_dir
from FuelLookup import *

GIS = r'C:\FireGUARD\data\GIS'
GIS_SHARE = common.CONFIG.get('FireGUARD', 'gis_share')
INPUT = os.path.join(GIS, "input")
GIS_ELEVATION = os.path.join(INPUT, "elevation")
GIS_FIRE = os.path.join(INPUT, 'fire')
GIS_FUELS = os.path.join(INPUT, 'fuels')
GIS_WATER = os.path.join(INPUT, 'water')
INTERMEDIATE = os.path.join(GIS, "intermediate")
DOWNLOADED = os.path.join(GIS, "downloaded")
OUTPUT = ensure_dir(os.path.join(INTERMEDIATE, "fuels"))
GENERATED = ensure_dir(os.path.join(GIS, "generated", "fuels"))
TIF_OUTPUT = ensure_dir(os.path.join(GENERATED, "out_{:03d}m".format(CELLSIZE_M)))
MAPPER_DIR = ensure_dir(os.path.join(OUTPUT, "mapper"))
BOUNDS_DIR = ensure_dir(os.path.join(OUTPUT, "01_bounds"))
WATER_DIR = ensure_dir(os.path.join(OUTPUT, "02_water"))
NTL_DIR = ensure_dir(os.path.join(OUTPUT, "03_ntl"))
WATER_BOUNDS_DIR = ensure_dir(os.path.join(OUTPUT, "04_waterbounds"))
NTL_FILL_DIR = ensure_dir(os.path.join(OUTPUT, "05_ntl_fill"))
FUEL_BASE_DIR = ensure_dir(os.path.join(OUTPUT, "06_fuel_base"))
FUEL_RASTER_DIR = ensure_dir(os.path.join(OUTPUT, "07_fuel_raster"))
FUEL_MOSAIC_DIR = ensure_dir(os.path.join(OUTPUT, "08_fuel_mosaic"))
FUEL_DIR = ensure_dir(os.path.join(OUTPUT, "09_fuel"))
FUEL_JOIN_DIR = ensure_dir(os.path.join(OUTPUT, "10_fuel_join"))
MAPPER_GDB = os.path.join(GIS_FUELS, "FuelGrid_FBP.gdb")

POLY_GDB = checkGDB(OUTPUT, "processed.gdb")
PROCESSED_GDB = checkGDB(OUTPUT, "processed_{:03d}m.gdb".format(CELLSIZE_M))
BOUNDS_GDB = checkGDB(BOUNDS_DIR, "bounds.gdb")

## NDD Non-sensitive data from share
NDD_NON = os.path.join(GIS_SHARE, "NDD", "GDDS-Internal-MNRF.gdb")

mask_LIO_gdb = os.path.join(OUTPUT, "{}_LIO.gdb")
PROVINCE = os.path.join(NDD_NON, "PROVINCE")
## DEM made by combining EarthEnv data into a TIFF
EARTHENV = os.path.join(GIS_ELEVATION, "EarthEnv.tif")
FIDE_INPUT = os.path.join(GIS_FUELS, "LIO", "FOREST_INSECT_DAMAGE_EVENT.shp")
FIDE = check_make(os.path.join(POLY_GDB, 'FIDE'), lambda _: arcpy.CopyFeatures_management(FIDE_INPUT, _))
DAMAGE = None

MNR_LAMBERT = arcpy.SpatialReference('Projected Coordinate Systems/National Grids/Canada/NAD 1983 CSRS Ontario MNR Lambert')
PROJECTION = MNR_LAMBERT

FIRE_DISTURBANCE = os.path.join(GIS_FIRE, r'FIRE_DISTURBANCE_AREA.shp')
DEM_BOX_SIZE_KM = 50
BUFF_DIST = "{} kilometers".format(DEM_BOX_SIZE_KM)
DEM_BOX = None

# NOTE: this only applies where there's no national layer or no LIO data
LIO_CELL_BUFFER = 50

# use this so that we process them sequentially
import collections
projections = collections.OrderedDict()
projections[14.5] = { 'CentralMeridian': -96.0 }
projections[15.0] = { 'CentralMeridian': -93.0 }
projections[15.5] = { 'CentralMeridian': -90.0 }
projections[16.0] = { 'CentralMeridian': -87.0 }
projections[16.5] = { 'CentralMeridian': -84.0 }
projections[17.0] = { 'CentralMeridian': -81.0 }
projections[17.5] = { 'CentralMeridian': -78.0 }
projections[18.0] = { 'CentralMeridian': -75.0 }

# base our projected zones off of UTM Zone 15N but change the Central Meridian for each
ZONES = projections.keys()

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--zones", help="any of {}".format(ZONES))
parser.add_argument("-m", action="store_true", help="create mapper data")
parser.add_argument("-c", action="store_true", help="copy to server")
parser.add_argument("--split", action="store_true", help="split output rasters")
parser.add_argument("--force", action="store_true", help="force generating fuels databases")
parser.add_argument("--fbp", action="store_true", help="update FBP classifications")
# HACK: do this so that if we manually set args while debugging they don't get overridden
try:
    if not args:
        args = parser.parse_args()
except:
    # this will throw if we haven't done this yet
    args = parser.parse_args()
    if 0 == len(''.join(sys.argv)):
        # this means we're in arcmap?
        #~ args.zones = '14.5,16.5'
        #~ args.zones = '15.0,17.0'
        #~ args.zones = '15.5,17.5'
        #~ args.zones = '16.0,18.0'
        #~ args.zones = '14.5'
        #~ args.zones = '15.0'
        #~ args.zones = '15.5'
        #~ args.zones = '16.0'
        #~ args.zones = '16.5'
        #~ args.zones = '17.0'
        #~ args.zones = '17.5'
        #~ args.zones = '18.0'
        args.m = True
        #~ args.fbp = True
        #~ args.c = True
        #~ args.force = True
#~ args.split = True
DO_COPY_TO_SERVER = args.c
DO_MAPPER = args.m
DO_SPLIT = args.split
FORCE = args.force
DO_FBP = args.fbp
if args.zones:
    if DO_COPY_TO_SERVER or DO_MAPPER:
        print("Can't run for specific zones if generating mapper or server output")
        sys.exit(-1)
    arg_zones = [float(x.strip()) for x in args.zones.split(',')]
    for x in arg_zones:
        if x not in ZONES:
            print("Invalid zone: " + str(x))
            print(parser.format_help())
            sys.exit(-1)
    ZONES = [x for x in ZONES if x in arg_zones]


# USA National Hydrography Dataset
# https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHD/National/HighResolution/GDB/NHD_H_National_GDB.zip
lakes_nhd = os.path.join(GIS_WATER, "NHD.gdb", "Hydrography", "NHDWaterbody")
lakes_nhd_area = os.path.join(GIS_WATER, "NHD.gdb", "Hydrography", "NHDArea")
canada = os.path.join(INPUT, "canada\\lpr_000b16a_e.shp")
ntl_2018 = os.path.join(GIS_FUELS, r'national\fuellayer\FBP_FuelLayer_wBurnscars.tif')

PROJECTION_BASE = arcpy.SpatialReference(3159).exportToString().replace("15N","{}N").replace("-93.0","{}")

# NOTE: use 645 instead of 650 because that's what it was before and we don't know why
dct_ntl = {
    98: 104,
    99: 103,
    101: 1,
    102: 2,
    103: 3,
    104: 4,
    105: 5,
    106: 6,
    107: 7,
    108: 13,
    109: 645,
    111: 950,
    113: 21,
    114: 22,
    115: 23,
    116: 31,
    118: 102,
    119: 101,
    120: 105,
    121: 101,
    122: 105,
}

dct_2018 = {}
# fix mixedwood not being generic
for x in xrange(0, 100, 1):
    dct_2018[400 + x] = 600 + x
    dct_2018[500 + x] = 600 + x
    dct_2018[700 + x] = 900 + x
    dct_2018[800 + x] = 900 + x
# fix D2 being used for lichen and mosses in the far north
dct_2018[12] = 105
# change D1 to D1/D2
dct_2018[11] = 13
for x in xrange(1, 1000):
    if not dct_2018.has_key(x):
        dct_2018[x] = x

# have these functions so we make sure we always use the right type when copying each type of raster
def copyFuel(in_raster, out_raster):
    arcpy.CopyRaster_management(in_raster, out_raster, pixel_type="16_BIT_UNSIGNED", nodata_value="0")


def copyDEM(in_raster, out_raster):
    arcpy.CopyRaster_management(in_raster, out_raster, pixel_type="16_BIT_SIGNED")


def copyAspect(in_raster, out_raster):
    arcpy.CopyRaster_management(in_raster, out_raster, pixel_type="16_BIT_UNSIGNED")


def copySlope(in_raster, out_raster):
    arcpy.CopyRaster_management(in_raster, out_raster, pixel_type="8_BIT_UNSIGNED")


def create_projection(zone):
    result = arcpy.SpatialReference()
    result.loadFromString(PROJECTION_BASE.format(zone, projections[zone]['CentralMeridian']))
    return result

def selectOverlap(base, intersect, output, makeEmpty=True):
    lyr = arcpy.CreateScratchName()
    arcpy.MakeFeatureLayer_management(base, lyr)
    arcpy.SelectLayerByLocation_management(lyr, "INTERSECT", intersect)
    count = int(arcpy.GetCount_management(lyr)[0])
    if makeEmpty or count > 0:
        arcpy.CopyFeatures_management(lyr, output)
    arcpy.Delete_management(lyr)
    if count == 0 and not makeEmpty:
        return None
    return output


def create_grid(zone):
    zone_fixed = '{}'.format(zone).replace('.', '_')
    def makeDEM(_):
        zone_dir = ensure_dir(os.path.join(BOUNDS_DIR, 'zone_{}'.format(zone_fixed)))
        # \1
        env_push()
        env_defaults(workspace=checkGDB(zone_dir, 'grids_{}m.gdb'.format(gridSize)),
                     cellSize=CELLSIZE_M)
        Projection = create_projection(zone)
        # determine extent in zone that we're looking for
        print("Changing projection to {}".format(Projection.name))
        arcpy.env.outputCoordinateSystem = Projection
        print("Creating {}m grid for {}".format(gridSize, Projection.name))
        province = project(PROVINCE, "province", Projection)
        bounds = check_make("bounds", lambda _: arcpy.Buffer_analysis("province", _, BUFF_DIST))
        print("Creating large grid for zone {}".format(zone))
        # create a grid that's got the core part of the zone without worry about edges since we'll have others for that
        # \2
        env_push()
        arcpy.env.outputCoordinateSystem = Projection
        zoneBounds = check_make("ZoneBounds", lambda _: arcpy.CreateFishnet_management(_,
                                                                                       "300000 4000000",
                                                                                       "300000 4000010",
                                                                                       "{}".format(bigGridSize_m),
                                                                                       "{}".format(bigGridSize_m),
                                                                                       "0",
                                                                                       "0",
                                                                                       "700000 7000000",
                                                                                       "NO_LABELS",
                                                                                       "300000 4000000 700000 7000000",
                                                                                       "POLYGON"))
        env_pop()
        # /2
        #~ outerBounds = check_make("OuterBounds", lambda _: arcpy.Dissolve_management("ZoneBounds", _, "", "", "MULTI_PART", "DISSOLVE_LINES"))
        boundClip = check_make("BoundClip", lambda _: arcpy.Clip_analysis(zoneBounds, bounds, _))
        finalBounds = check_make("Area", lambda _: arcpy.MinimumBoundingGeometry_management(boundClip, _, "ENVELOPE", "ALL"))
        boundsBuffer = check_make("BoundsBuffer", lambda _: arcpy.Buffer_analysis(finalBounds, _, "20 Kilometers"))
        zoneGrid = check_make("ZoneGrid", lambda _: selectOverlap(zoneBounds, boundsBuffer, _))
        zoneBuffer = check_make("ZoneBuffer", lambda _: arcpy.Buffer_analysis(zoneGrid, _, "20 Kilometers", dissolve_option="ALL"))
        DEM_clip = calc("DEM_clip", lambda _: clip_raster_box(EARTHENV, zoneBuffer, _), buildPyramids=False)
        def mkMask(input):
            full_extent = arcpy.Describe(input).extent
            print(full_extent)
            # use the bounding box of the first big grid cell that isn't missing cells inside (as per above)
            xMin = int(round(full_extent.XMin / gridSize, 0)) * gridSize
            yMin = int(round(full_extent.YMin / gridSize, 0)) * gridSize
            xMax = int(round(full_extent.XMax / gridSize, 0)) * gridSize
            yMax = int(round(full_extent.YMax / gridSize, 0)) * gridSize
            assert (xMin < xMax)
            assert (yMin < yMax)
            print("Bounds for raster are: ({}, {}), ({}, {})".format(xMin, yMin, xMax, yMax))
            mask = CreateConstantRaster(0, "INTEGER", gridSize, full_extent)
            arcpy.DefineProjection_management(mask, Projection.exportToString())
            return mask
        mask = calc("Zone", lambda _: mkMask(zoneGrid))
        mask = calc("Buffer", lambda _: mkMask(zoneBuffer))
        # \2
        env_push()
        env_defaults(mask=mask,
                     snapAndExtent=mask)
        arcpy.env.outputCoordinateSystem = Projection
        dem = check_make("DEM_project", lambda _: project_raster(DEM_clip, _, gridSize, "BILINEAR", Projection))
        checkGDB(os.path.dirname(_))
        copyDEM(dem, _)
        env_pop()
        # /2
        env_pop()
        # /1
    return check_make(os.path.join(GENERATED, "dem_{:03d}m.gdb".format(CELLSIZE_M), "dem_{}".format(zone_fixed)), makeDEM)


def make_grid(zones, showIntermediate=False):
    print("Generating grid for zones {}".format(zones))
    origAddOutputsToMap = arcpy.env.addOutputsToMap
    arcpy.env.addOutputsToMap = showIntermediate
    outputs = []
    i = 0
    for zone, params in projections.iteritems():
        if zone in zones:
            i += 1
            print("Processing zone {} of {}".format(i, len(zones)))
            projections[zone]['ZoneGrid'] = create_grid(zone)
            outputs += [projections[zone]['ZoneGrid']]
    arcpy.env.addOutputsToMap = origAddOutputsToMap

def makeWater(province, water_projected, erase, orig=None, clear=True, sql=None, clip=None):
    if not orig:
        orig = os.path.join(GIS_WATER, "canvec_50K_{}_Hydro.gdb\\waterbody_2".format(province))
    last = orig
    if clip:
        last = check_make("water_{}_clip".format(province), lambda _: arcpy.Clip_analysis(last, clip, _))
    if sql:
        last = check_make("water_{}_select".format(province), lambda _: arcpy.Select_analysis(last, _, sql))
    if clear:
        last = check_make("water_{}_no_fields".format(province), lambda _: clearData(last, _))
    projected = os.path.join(water_projected, "WATER_{}_project".format(province))
    last = project(last, projected)
    last = check_make("water_{}".format(province), lambda _: arcpy.Erase_analysis(last, erase, _))
    return last

def mkFuel(zone_name, buffer, fuel_buffer, projection):
    grid_gdb = checkGDB(ensure_dir(os.path.join(BOUNDS_DIR, zone_name)), 'grids_{}m.gdb'.format(gridSize))
    # \1
    env_push()
    env_defaults(mask=fuel_buffer,
                 snapAndExtent=buffer)
    # \2
    env_push()
    env_defaults(workspace=checkGDB(ensure_dir(os.path.join(NTL_DIR, zone_name)), 'ntl_{}m.gdb'.format(gridSize)), mask="", extent="", snapRaster=buffer, cellSize=CELLSIZE_M)
    ntl_clip = calc("ntl_clip", lambda _: clip_raster_box(ntl_2018_reclassify, fuel_buffer, _), buildPyramids=False)
    # keep entire grid because we need to fill in from outside
    ntl_project = calc("ntl_project", lambda _: project_raster(ntl_clip, _, cellsize_m=CELLSIZE_M, projection=projection))
    ntl_nowater = calc("ntl_nowater", lambda _: SetNull(ntl_project == 102, ntl_project))
    env_pop()
    # /2
    # \2
    env_push()
    env_defaults(workspace=checkGDB(ensure_dir(os.path.join(WATER_DIR, zone_name)), 'water_{}m.gdb'.format(gridSize)))
    water_select = check_make("water_select", lambda _: selectOverlap(WATER, fuel_buffer, _))
    water_proj = project(water_select, "water_proj", projection)
    water_raster = calc("water_raster", lambda _: arcpy.FeatureToRaster_conversion(water_proj, "gridcode", _, CELLSIZE_M))
    env_pop()
    # /2
    env_push()
    env_defaults(mask="", snapAndExtent="", workspace=checkGDB(ensure_dir(os.path.join(WATER_BOUNDS_DIR, zone_name)), 'water_{}m.gdb'.format(gridSize)))
    bounds_water = calc("bounds_water", lambda _: Con(IsNull(ntl_project), ntl_project, Con(IsNull(water_raster), ntl_nowater, water_raster)))
    bounds_mask = calc_mask("bounds_mask", bounds_water)
    FILL_SIZE = 10
    bounds_filled = calc("bounds_filled", lambda _: arcpy.sa.Con(arcpy.sa.IsNull(bounds_mask),arcpy.sa.FocalStatistics(bounds_mask,
                                                                   arcpy.sa.NbrRectangle(FILL_SIZE, FILL_SIZE),'MAJORITY'), bounds_mask))
    # shrink back down so edges don't end up with euclidean
    bounds_shrink = calc("bounds_shrink", lambda _: Shrink(bounds_filled, FILL_SIZE / 2, [0]))
    # need to fill in vertical edges
    bounds_all = calc("bounds_all", lambda _: Con(IsNull(water_raster), bounds_shrink, water_raster))
    bounds_nowater = calc("bounds_nowater", lambda _: SetNull(bounds_all == 102, bounds_all))
    env_pop()
    # /2
    # \2
    env_push()
    env_defaults(mask=bounds_nowater, snapAndExtent=buffer,
                 workspace=checkGDB(ensure_dir(os.path.join(NTL_FILL_DIR, zone_name)), 'ntl_{}m.gdb'.format(gridSize)))
    fuel_euclidean = check_make("fuel_euclidean", lambda _: arcpy.gp.EucAllocation_sa(ntl_nowater, _, "", "", CELLSIZE_M, "Value", "fuel_euclidean_distance", "fuel_euclidean_direction"))
    # \3
    env_push()
    env_defaults(snapAndExtent=buffer, mask="")
    fuel_filled = calc("fuel_filled", lambda _: Con(IsNull(water_raster), fuel_euclidean, water_raster))
    # /3
    env_pop()
    # /2
    env_pop()
    fuel_gdb = checkGDB(ensure_dir(os.path.join(FUEL_DIR, zone_name)), 'fuel_{}m.gdb'.format(gridSize))
    # \2
    env_push()
    env_defaults(workspace=fuel_gdb, mask=buffer, snapAndExtent=buffer)
    def runLIO(number, name):
        grid_dir = ensure_dir(os.path.join(os.path.dirname(fuel_gdb), name))
        print("Finding {} data".format(name))
        # convert to raster
        def ensureLIO(_):
            base_gdb = os.path.join(ensure_dir(os.path.join(FUEL_BASE_DIR, zone_name)), "{}_{}.gdb".format(number, name))
            # elev_out = os.path.join(GENERATED, 'elev_{:03d}m.tif'.format(CELLSIZE_M))
            # using ontario data actually seems to make DEM worse since it's weird around the provincial borders
            # we don't really need floating point precision??
            # elev_out = check_make(elev_out, lambda _: copyDEM(EarthEnv, _))
            features = sorted(getFeatures(mask_LIO_gdb.format(name)))
            # find overlap with LIO layers
            def makeBaseGDB(_):
                env_push()
                env_defaults(workspace=checkGDB(_))
                for f in features:
                    def doLayer(_):
                        #~ selectOverlap(f, fuel_buffer, _, False)
                        #~ (base, intersect, output, makeEmpty=True)
                        base = f
                        intersect = fuel_buffer
                        output = _
                        makeEmpty = False
                        lyr = arcpy.CreateScratchName()
                        arcpy.MakeFeatureLayer_management(base, lyr)
                        arcpy.SelectLayerByLocation_management(lyr, "INTERSECT", intersect)
                        # remove invalid
                        arcpy.SelectLayerByAttribute_management(lyr, "REMOVE_FROM_SELECTION", "POLYTYPE = 'XXX'")
                        count = int(arcpy.GetCount_management(lyr)[0])
                        if makeEmpty or count > 0:
                            arcpy.CopyFeatures_management(lyr, output)
                            # repair this because when it was copied it was projected
                            arcpy.RepairGeometry_management(lyr)
                        arcpy.Delete_management(lyr)
                        if count == 0 and not makeEmpty:
                            return None
                        return output
                    check_make(os.path.basename(f), doLayer)
                env_pop()
            grid_workspace = os.path.join(FUEL_RASTER_DIR, zone_name, "{}_{}_{:03d}m".format(number, name, CELLSIZE_M))
            base_gdb = check_make(base_gdb, makeBaseGDB, FORCE and not arcpy.Exists(grid_workspace))
            def makeGridGDB(_):
                # call this every time we make this so that we don't need to re-run it outside and get polygons again
                if DO_FBP:
                    fuelconversion.FRI2FBP2016(base_gdb)
                env_push()
                # clear this because some rasters crash
                env_defaults(workspace=ensure_dir(_), mask=None, extent=None, cellSize=None, pyramid=None)
                arcpy.env.outputCoordinateSystem = None
                env_push()
                # This crashes when trying to use gdb, so use TIFFs
                env_clear()
                arcpy.env.mask = None
                arcpy.env.snapRaster = buffer
                for f in sorted(getFeatures(base_gdb)):
                    if countRows(f) == 0:
                        raise Exception("Error - no features in input {}".format(f))
                    def mkRaster(_):
                        arcpy.FeatureToRaster_conversion(f, "FBPvalue", _, CELLSIZE_M)
                    to_raster = os.path.join(_, os.path.basename(f) + ".tif")
                    print(to_raster)
                    r = calc(to_raster, mkRaster, buildPyramids=False)
                env_pop()
                env_pop()
            # crashes when trying to mosaic when using gdb, so use TIFF
            grid_workspace = check_make(grid_workspace, makeGridGDB, FORCE)
            env_push()
            env_defaults(workspace=ensure_dir(os.path.join(FUEL_MOSAIC_DIR, zone_name, "{}_{}_filter_{:03d}m".format(number, name, CELLSIZE_M))))
            def mkUnfiltered(_):
                # HACK: assume something made it into the raster already
                rasters = sorted(getRasters(grid_workspace))
                print("Adding {}".format(raster_path(rasters[0])))
                copyFuel(rasters[0], _)
                for r in rasters[1:]:
                    print("Adding {}".format(raster_path(r)))
                    arcpy.Mosaic_management(r, _)
            # NOTE: these rasters look really wrong along the edges but the next step cleans that up
            unfiltered = calc(os.path.join(arcpy.env.workspace, 'unfiltered.tif'), mkUnfiltered)
            # keep unclassified but not non-fuel or Unknown
            filtered = calc('filtered.tif', lambda _: SetNull(unfiltered == 101, SetNull(unfiltered == 103, unfiltered)))
            filter_mask = calc_mask('mask_filtered.tif', filtered)
            filter_buffer = calc('buffer_filtered.tif', lambda _: Expand(filter_mask, LIO_CELL_BUFFER, [0]))
            # remove water because we trust the polygons we used before more
            nowater = calc('nowater.tif', lambda _: SetNull(filtered == 102, filtered))
            env_pop()
            env_push()
            env_defaults(mask=filter_buffer)
            fuel_euclidean = calc("fuel_euclidean", lambda _: arcpy.gp.EucAllocation_sa(nowater, _, "", "", CELLSIZE_M, "Value", "fuel_euclidean_distance", "fuel_euclidean_direction"))
            env_pop()
            # override everything with water, but only use the euclidean where the original non-euclidean national layer doesn't exist
            return calc(_, lambda _: Con(IsNull(water_raster), Con(IsNull(ntl_nowater), fuel_euclidean, nowater), water_raster), FORCE)
        fuel_lio_only = check_make("fuel_{}_only".format(name), ensureLIO, FORCE)
        return fuel_lio_only
    fuel_last = fuel_efri_only = runLIO(1, 'efri')
    # /2
    env_pop()
    env_push()
    env_defaults(workspace=checkGDB(ensure_dir(os.path.join(FUEL_JOIN_DIR, zone_name)), 'fuel_{}m.gdb'.format(gridSize)))
    fuel_last = fuel_efri_ntl = calc('fuel_efri_ntl', lambda _: Con(IsNull(fuel_efri_only), fuel_filled, fuel_efri_only), FORCE)
    fires = calc("fires", lambda _: arcpy.FeatureToRaster_conversion(FIRE_DISTURBANCE, "FIRE_YEAR", _, CELLSIZE_M))
    cur_year = datetime.datetime.now().year
    fuel_years = [101, 104, 104, 105, 105, 625, 625, 625, 625, 625]
    fire_years = []
    for i in xrange(len(fuel_years)):
        fire_years.append(calc("fires_{:02d}".format(i), lambda _: Con(fires == (cur_year - i), fuel_years[i])).catalogPath)
    water = calc("water", lambda _: SetNull(fuel_efri_ntl != 102, fuel_efri_ntl))
    inputs = ';'.join([water.catalogPath] + fire_years + [fuel_efri_ntl.catalogPath])
    # HACK: crashing when we try to do this with calc()
    #~ fuel_last = fuel_fires = calc("fuel_fires", lambda _: arcpy.MosaicToNewRaster_management(inputs, arcpy.env.workspace, _, "", "32_BIT_SIGNED", "", 1, "FIRST"))
    if not arcpy.Exists(os.path.join(arcpy.env.workspace, "fuel_fires")):
        arcpy.MosaicToNewRaster_management(inputs, arcpy.env.workspace, "fuel_fires", "", "32_BIT_SIGNED", "", 1, "FIRST")
    fuel_last = fuel_fires = os.path.join(arcpy.env.workspace, "fuel_fires")
    env_pop()
    return fuel_last


def create_fuel(zone):
    print("Creating fuel for zone {}".format(zone))
    fuel_gdb = checkGDB(GENERATED, "fuel_{:03d}m.gdb".format(CELLSIZE_M))
    fuel_final = os.path.join(fuel_gdb, "fuel_{}".format(zone).replace('.', '_'))
    fuel_tif = os.path.join(TIF_OUTPUT, "fuel_{:03d}m_{}.tif".format(CELLSIZE_M, str(zone).replace('.', '_')))
    slope_tif = os.path.join(TIF_OUTPUT, "slope_{:03d}m_{}.tif".format(CELLSIZE_M, str(zone).replace('.', '_')))
    aspect_tif = os.path.join(TIF_OUTPUT, "aspect_{:03d}m_{}.tif".format(CELLSIZE_M, str(zone).replace('.', '_')))
    if not DO_SPLIT and arcpy.Exists(fuel_final) and arcpy.Exists(fuel_tif) and arcpy.Exists(slope_tif) and arcpy.Exists(aspect_tif):
        return fuel_final
    zone_name = 'zone_{}'.format(zone).replace('.', '_')
    grid_gdb = checkGDB(ensure_dir(os.path.join(BOUNDS_DIR, zone_name)), 'grids_{}m.gdb'.format(gridSize))
    env_push()
    env_defaults(workspace=grid_gdb,
                 cellSize=CELLSIZE_M)
    projection = create_projection(zone)
    arcpy.env.outputCoordinateSystem = projection
    # determine extent in zone that we're looking for
    print("Changing projection to {}".format(projection.name))
    buffer = os.path.join(arcpy.env.workspace, "Zone")
    fuel_buffer = os.path.join(arcpy.env.workspace, "ZoneBuffer")
    def check_copy_fuel(_):
        fuel = mkFuel(zone_name, buffer, fuel_buffer, projection)
        copyFuel(fuel, _)
    fuel_final = check_make(fuel_final, check_copy_fuel)
    fuel_tif = calc(fuel_tif, lambda _: copyFuel(fuel_final, _))
    env_push()
    env_defaults(snapAndExtent=fuel_tif)
    dem_gdb = checkGDB(GENERATED, "dem_{:03d}m.gdb".format(CELLSIZE_M))
    dem_out = os.path.join(dem_gdb, "dem_{}".format(zone).replace('.', '_'))
    dem_tif = os.path.join(TIF_OUTPUT, "dem_{:03d}m_{}.tif".format(CELLSIZE_M, str(zone).replace('.', '_')))
    dem_tif = calc(dem_tif, lambda _: copyDEM(dem_out, _))
    slope_float = os.path.join(grid_gdb, "slope_{}".format(zone).replace('.', '_'))
    slope_float = calc(slope_float, lambda _: arcpy.Slope_3d(dem_out, _, "PERCENT_RISE"))
    slope_gdb = checkGDB(GENERATED, "slope_{:03d}m.gdb".format(CELLSIZE_M))
    slope_out = os.path.join(slope_gdb, "slope_{}".format(zone).replace('.', '_'))
    slope_out = calc(slope_out, lambda _: copySlope(slope_float, _))
    slope_tif = calc(slope_tif, lambda _: copySlope(slope_out, _))
    aspect_float = os.path.join(grid_gdb, "aspect_{}".format(zone).replace('.', '_'))
    aspect_float = calc(aspect_float, lambda _: arcpy.Aspect_3d(dem_out, _))
    aspect_gdb = checkGDB(GENERATED, "aspect_{:03d}m.gdb".format(CELLSIZE_M))
    aspect_out = os.path.join(aspect_gdb, "aspect_{}".format(zone).replace('.', '_'))
    aspect_out = calc(aspect_out, lambda _: copyAspect(aspect_float, _))
    aspect_tif = calc(aspect_tif, lambda _: copyAspect(aspect_out, _))
    env_pop()
    if DO_SPLIT:
        split_dir = os.path.join(TIF_OUTPUT, "split")
        ensure_dir(split_dir)
        # can't have more than 32767 rows or columns, but try to make them square
        # cut things up a lot but make them overlap significantly so we can always find an area centered on the fire
        # NOTE: 1.0 ha cells end up with 4001 pixel wide tiffs, so set based on splitting those up vertically
        #~ center_size = 4001.0 / 2
        #~ tilesize = 2.0 * center_size
        #~ overlap = center_size
        #~ # if one tile spans the entire width then don't split it
        #~ # if not 1 tile then make sure it's even # so snapraster still works
        #~ num_tile_columns = 2 * (int(math.ceil(slope_tif.width / float(center_size))) / 2) if tilesize < slope_tif.width else 1
        #~ num_tile_rows = 2 * (int(math.ceil(slope_tif.height / float(center_size))) / 2) if tilesize < slope_tif.height else 1
        # 14.5 1333.66666667 4001.0 1332 1 7
        # 15.0 1333.66666667 4001.0 1332 1 9
        # 15.5
        # 16.0
        # 16.5
        # 17.0
        # 17.5
        # 18.0
        # want to make squares
        DEFAULT_TILE_SIZE = 4002
        center_size = DEFAULT_TILE_SIZE / 3.0
        tilesize = int(3.0 * center_size)
        # make sure this is even so we stay on same snap
        overlap = 2 * int(center_size / 2)
        # if one tile spans the entire width then don't split it
        #~ num_tile_columns = int(math.ceil(slope_tif.width / float(center_size))) if tilesize < slope_tif.width else 1
        #~ num_tile_rows = int(math.ceil(slope_tif.height / float(center_size))) if tilesize < slope_tif.height else 1
        #~ num_tile_columns = 2 * (int(math.ceil(slope_tif.width / float(center_size))) / 2) if tilesize < slope_tif.width else 1
        #~ num_tile_rows = 2 * (int(math.ceil(slope_tif.height / float(center_size))) / 2) if tilesize < slope_tif.height else 1
        #~ num_rasters = "{} {}".format(num_tile_columns, num_tile_rows)
        #~ print(zone, center_size, tilesize, overlap, num_tile_columns, num_tile_rows)
        #~ print("Splitting into {} tiles".format(num_rasters.replace(' ', 'x')))
        tile_size = "{} {}".format(DEFAULT_TILE_SIZE, DEFAULT_TILE_SIZE)
        print("Splitting into {} tiles".format(tile_size.replace(" ", "x")))
        def doSplit(r):
            arcpy.SplitRaster_management(r, split_dir, r.name.replace('.tif', '__'), "SIZE_OF_TILE", "TIFF", tile_size=tile_size, overlap=overlap)
        env_push()
        env_defaults(snapRaster=fuel_tif)
        doSplit(fuel_tif)
        doSplit(dem_tif)
        doSplit(slope_tif)
        doSplit(aspect_tif)
        env_pop()
    env_pop()
    return fuel_final

def makeDamage(_):
    lyr = arcpy.CreateScratchName()
    def mkList(values):
        return '(' + ','.join(map(lambda x: "'" + x + "'", values)) +')'
    damage_types = mkList(['Jack Pine Budworm' , 'Spruce Budworm' , 'Misc Beetle Damage to Jack Pine'])
    rankings = mkList(['Severe', 'Mortality'])
    mask = '"INSECT" IN {} AND "EVENT_YEAR" >= {} AND "RANKING" IN {}'
    filter = mask.format(damage_types, datetime.datetime.now().year - 10, rankings)
    arcpy.MakeFeatureLayer_management(FIDE, lyr, filter)
    arcpy.CopyFeatures_management(lyr, _)
    arcpy.Delete_management(lyr)
    arcpy.AddField_management("damage", "M3_Value", "SHORT")
    arcpy.CalculateField_management("damage", "M3_Value", "300", "PYTHON")
    return _

def getColumns(_):
    return [x.name for x in arcpy.ListFields(_)]

def countRows(_):
    count = 0
    with arcpy.da.SearchCursor(_, [arcpy.Describe(_).OIDFieldName]) as cursor:
        for row in cursor:
            count += 1
    return count

def round_to_nearest(x, base):
    return int(base * math.ceil(float(x) / base))

def getName(_):
    return os.path.basename(str(_))

def fixColumnNames(src, fields):
    actuals = getColumns(src)
    lower = map(lambda _: _.lower(), actuals)
    real = []
    for f in fields:
        assert (f.lower() in lower), "Missing field {} is required".format(f)
        real.append(actuals[lower.index(f.lower())])
    return real

def copyByFields(src, dest, fields):
    maps = arcpy.FieldMappings()
    real_fields = fixColumnNames(src, fields)
    for f in real_fields:
        map = arcpy.FieldMap()
        map.addInputField(src, f)
        maps.addFieldMap(map)
    arcpy.FeatureClassToFeatureClass_conversion(src, os.path.dirname(dest), os.path.basename(dest), "#", maps)

def percentile(n, pct):
    return int(float(n) * float(pct) / 100.0)

def fixMapper(_):
    zone_name = "lambert"
    zone_dir = ensure_dir(os.path.join(OUTPUT, zone_name))
    grid_gdb = checkGDB(zone_dir, 'grids_{}m.gdb'.format(gridSize))
    env_push()
    env_defaults(workspace=grid_gdb,
                 cellSize=CELLSIZE_M)
    arcpy.env.outputCoordinateSystem = PROJECTION
    # determine extent in zone that we're looking for
    print("Changing projection to {}".format(PROJECTION.name))
    fuel = mkFuel(zone_name, buffer, DEM_BOX, PROJECTION)
    fuel_final = check_make("fuel_final", lambda _: copyFuel(fuel, _))
    fuel = check_make(os.path.join(checkGDB(GENERATED, "fuel_{:03d}m.gdb".format(CELLSIZE_M)), "fuel"), lambda _: copyFuel(fuel, _))
    # don't want this in the directory with everything else so put it in parent directory
    fuel_tif = calc(os.path.join(os.path.dirname(TIF_OUTPUT), "fuel_{:03d}m_{}.tif".format(CELLSIZE_M, 'lambert')), lambda _: copyFuel(fuel_final, _))
    env_pop()
    MAPPER_TMP = checkGDB(MAPPER_DIR, "mapper.gdb")
    mapper_gdb = checkGDB(OUTPUT, "FuelGrid_FBP.gdb")
    GCS_WGS_1984 = arcpy.SpatialReference(4326)
    fuel_wcgs_84 = calc(os.path.join(mapper_gdb, 'fuel_{:03d}m'.format(CELLSIZE_M)), lambda _: project_raster(fuel_final, _, projection=GCS_WGS_1984))
    features = sorted(getFeatures(MAPPER_GDB))
    env_push()
    env_defaults(workspace=MAPPER_TMP)
    zooms = {}
    for f in features:
        if '_Point' in f:
            print("Processing " + f)
            base = f.replace('_Point', '')
            if base not in features:
                print("ERROR: Missing polygon feature for points")
            zoom = float(os.path.basename(base).replace('Fuel_', '').replace('00', '0.').replace('k', ''))
            zooms[zoom] = { 'point': f, 'base': base }
    # start from smallest pixel size and then work from there
    # don't just use the base data every time because then we get M1/M2 along coast at 40k even though it's C2 until then
    fuel = Raster(fuel_final)
    fuel_nowater = calc("fuel_nowater", lambda _: SetNull(fuel == 102, fuel))
    arcpy.BuildRasterAttributeTable_management(fuel_nowater, "Overwrite")
    # figure out what values are in the raster
    with arcpy.da.SearchCursor("fuel_nowater", "VALUE") as cursor:
        unique_values = set(row[0] for row in cursor)
    #
    fuelLookup = FuelLookup(os.path.join(HOME_DIR, 'fuel.lut'))
    fuel_m3m4 = fuelLookup.makeM3M4(fuel_nowater, "fuel_m3m4")
    def mkFuelPDF(_):
        # after we do that then everything that's left is the PDF once we % 100
        fuel_pdf = fuel_m3m4 % 100
        fuel_pdf.save(_)
    fuel_pdf = calc("fuel_pdf", mkFuelPDF)
    #
    fuel_conifer = fuelLookup.makeConifer(fuel_nowater, "fuel_conifer")
    fuel_deciduous = fuelLookup.makeDeciduous(fuel_nowater, "fuel_deciduous")
    fuel_mixedwood = fuelLookup.makeMixedwood(fuel_nowater, "fuel_mixedwood")
    #
    # for determining PC value we need to look at any fuels that contain conifer and ignore the rest
    def mkFuelPC(_):
        # NOTE: M3/M4 are currently calculated as all conifer is dead so we're counting the whole PDF as PC
        fuel_pc = Con(IsNull(fuel_conifer),
                        Con(IsNull(fuel_deciduous),
                                Con(IsNull(fuel_mixedwood),
                                    fuel_mixedwood,
                                    # all mixedwood cells considered as whatever PC they are
                                    fuel_mixedwood % 100),
                                # all deciduous cells considered as 0 PC
                                0),
                        # all conifer cells considered as 100 PC
                        100)
        fuel_pc.save(_)
    fuel_pc = calc("fuel_pc", mkFuelPC)
    #
    # remove non-fuels but keep everything else the same
    def mkFuelBase(_):
        src = Raster(fuel_final)
        fuel_base = Con(IsNull(src),
                        src,
                        Con(src > 100,
                            Con(src < 200,
                                Con(src == 102, 102, 101),
                                src
                                ),
                            src
                            )
                        )
        # keep 101 here because we want it to be the backup if the other raster has nothing
        fuel_base.save(_)
        arcpy.DefineProjection_management(fuel_base, PROJECTION)
        return fuel_base
    fuel_base = calc("fuel_base", mkFuelBase)
    # we want to make simplified fuels raster so that majority captures different pc and pdf
    def mkFuelSimple(_):
        src = fuel_nowater
        fuel_simple = Con(IsNull(src),
                        src,
                        Con(src > 100,
                            Con(src < 200,
                                101,
                                10 * (src / 100)
                                ),
                            src
                            )
                        )
        # don't want these included in the majority
        fuel_simple = SetNull(fuel_simple == 101, fuel_simple)
        fuel_simple.save(_)
        arcpy.DefineProjection_management(fuel_simple, PROJECTION)
        return fuel_simple
    fuel_simple = calc("fuel_simple", mkFuelSimple)
    fixed_no_nonfuel = fuel_simple
    fixed_simple = fuel_base
    for_simple = fuel_simple
    for zoom in sorted(zooms.keys()):
        base = zooms[zoom]['base']
        point = zooms[zoom]['point']
        suffix = str(zoom).replace('.', '_')
        gdb = checkGDB(MAPPER_DIR, "mapper_{}.gdb".format(suffix))
        mask = os.path.join(gdb, "{}_{}".format('{}', suffix))
        # want to use result of this for next level of zoom
        # FIX: works in arcmap but not commandline?
        water_majority = calc(mask.format('water_majority'), lambda _: arcpy.gp.ZonalStatistics_sa(base, "OBJECTID", fixed_simple, _, "MAJORITY", "DATA"))
        # revert back to fixed_no_nonfuel as the base so that points that are outside of higher zooms come back in
        for_simple = calc(mask.format('simple'), lambda _: arcpy.gp.ZonalStatistics_sa(base, "OBJECTID", fixed_no_nonfuel, _, "MAJORITY", "DATA"))
        # put water back in for areas that have no fuel at all
        fixed_simple = calc(mask.format('fixed_simple'), lambda _: Con(IsNull(for_simple), Con(IsNull(water_majority), fuel_simple, water_majority), for_simple))
        fixed_no_nonfuel = calc(mask.format('fixed_no_nonfuel'), lambda _: SetNull(fixed_simple == 101, SetNull(fixed_simple == 102, fixed_simple)))
        pc = calc(mask.format('pc'), lambda _: arcpy.gp.ZonalStatistics_sa(base, "OBJECTID", fuel_pc, _, "MEAN", "DATA"))
        pdf = calc(mask.format('pdf'), lambda _: arcpy.gp.ZonalStatistics_sa(base, "OBJECTID", fuel_pdf, _, "MEAN", "DATA"))
        # # concerned about showing areas as D1 when there's M1/M2 in them too
        # calc(majority_nd, lambda _: arcpy.gp.ZonalStatistics_sa(base, "fueltype", fuel_nodeciduous, _, "MAJORITY", "DATA"))
        # rasters = [fixed_majority, fixed_simple, pc, pdf]
        rasters = [fixed_simple, pc, pdf]
        FINAL_COLUMNS = ['Id', 'fueltype', 'DegOfModifier', 'FBPkey', 'ISI']
        def removeExtra(_, keep_columns=None):
            if not keep_columns:
                keep_columns = list(FINAL_COLUMNS)
            # have to keep the object id field but don't want to tie it to a specific name
            keep_columns += [arcpy.Describe(_).OIDFieldName, 'Shape']
            keep_columns = map(lambda x: x.lower(), keep_columns)
            # check against lower case so that we don't miss things with wrong casing
            extra_columns = [x for x in getColumns(_) if x.lower() not in keep_columns]
            if len(extra_columns) > 0:
                arcpy.DeleteField_management(_, ';'.join(extra_columns))
        def mkProj(_):
            project(point, _, MNR_LAMBERT)
            removeExtra(_)
        proj_point = check_make(os.path.join(gdb, os.path.basename(point) + "_proj"), mkProj)
        def mkName(_):
            return proj_point.replace('Point_proj', _)
        def mkExtracted(base, points):
            def doMkExtracted(_):
                arcpy.gp.ExtractValuesToPoints_sa(points, base, _, "NONE", "VALUE_ONLY")
                removeExtra(_, ['Id', 'RASTERVALU'])
                arcpy.AlterField_management(_, 'RASTERVALU', base.name)
            return [os.path.basename(base.name),
                     check_make(mkName(base.name), doMkExtracted)]
        simple_points = mkExtracted(fixed_simple, proj_point)
        def mkFiltered(_, value):
            def doMkFiltered(_):
                tmp = arcpy.CreateScratchName(workspace='in_memory')
                src = simple_points[1]
                fields = ['Id']
                arcpy.MakeFeatureLayer_management(src, tmp, '"{}" = {}'.format(simple_points[0], value))
                copyByFields(tmp, _, ['Id'])
                arcpy.Delete_management(tmp)
            return check_make(_, doMkFiltered)
        m1m2_points = mkFiltered(mkName('m1m2'), 60)
        pc_points = mkExtracted(pc, m1m2_points)
        assert(countRows(m1m2_points) == countRows(pc_points[1])), "Invalid number of percent conifer points"
        m3m4_points = mkFiltered(mkName('m3m4'), 90)
        pdf_points = mkExtracted(pdf, m3m4_points)
        assert(countRows(m3m4_points) == countRows(pdf_points[1])), "Invalid number of percent dead fir points"
        extracted = [simple_points, pc_points, pdf_points]
        #~ _ = os.path.join(mapper_gdb, os.path.basename(point))
        def makeFinal(_):
            env_push()
            arcpy.env.outputCoordinateSystem = None
            # don't use check_make since we already know we called it
            copyByFields(point, _, FINAL_COLUMNS)
            env_pop()
            columns = ["Id", "fueltype", "DegOfModifier"]
            def getIndex(_):
                return columns.index(getName(_))
            count = countRows(_)
            print('Processing {} rows'.format(count))
            i = 0
            next_break = 0
            print("Opening {} for update".format(_))
            with arcpy.da.UpdateCursor(_, columns, sql_clause=['', "ORDER BY Id"]) as cursor:
                print("Opening {} for read".format(simple_points[1]))
                with arcpy.da.SearchCursor(simple_points[1], ['Id', simple_points[0]], sql_clause=['', "ORDER BY Id"]) as cur_simple:
                    print("Opening {} for read".format(pc_points[1]))
                    with arcpy.da.SearchCursor(pc_points[1], ['Id', pc_points[0]], sql_clause=['', "ORDER BY Id"]) as cur_pc:
                        print("Opening {} for read".format(pdf_points[1]))
                        with arcpy.da.SearchCursor(pdf_points[1], ['Id', pdf_points[0]], sql_clause=['', "ORDER BY Id"]) as cur_pdf:
                            print("Updating...")
                            indexId = 0
                            indexData = 1
                            for row in cursor:
                                #~ print("DST: " + str(row))
                                if i >= next_break:
                                    cur_pct = int(i * 100.0 / count)
                                    next_break = (cur_pct + 2) * count / 100
                                    sys.stdout.write(str(cur_pct) if (0 == (cur_pct % 10)) else '.')
                                i += 1
                                s = cur_simple.next()
                                #~ print("SRC: " + str(s))
                                assert (s[indexId] == row[indexId]), "Fuel data is invalid: {}\n{}\n".format(str(s), str(row))
                                f = s[indexData]
                                # now we need to translate those values into text
                                fuel = fuelLookup.by_value[f]
                                if 'O-1' in fuel:
                                    fuel = 'O-1'
                                elif 'D-' in fuel:
                                    fuel = 'D-1'
                                # use lookups just to make indices obvious
                                row[columns.index("fueltype")] = fuel
                                param = 0
                                deg = ""
                                if 'M-1' in fuel or 'M-2' in fuel:
                                    # need percent conifer
                                    row_pc = cur_pc.next()
                                    #~ print("PC:  " + str(row_pc))
                                    assert (row_pc[indexId] == row[indexId]), "Percent Conifer data is invalid: {}\n{}\n".format(str(row_pc), str(row))
                                    param = row_pc[indexData]
                                    deg = round_to_nearest(param, 25) if param else 0
                                elif 'M-3' in fuel or 'M-4' in fuel:
                                    # need percent dead fir
                                    row_pdf = cur_pdf.next()
                                    #~ print("PDF: " + str(row_pdf))
                                    assert (row_pdf[indexId] == row[indexId]), "Percent Dead Fir data is invalid: {}\n{}\n".format(str(row_pdf), str(row))
                                    param = row_pdf[indexData]
                                    deg = round_to_nearest(param, 30) if param else 0
                                    if 90 == deg:
                                        deg = 100
                                row[columns.index("DegOfModifier")] = deg
                                cursor.updateRow(row)
            print("100\nDone updating {} rows".format(i))
            assert (i == count), "Didn't update the right number of rows ({} of {})".format(i, count)
        final_point = check_make(os.path.join(mapper_gdb, os.path.basename(point)), makeFinal)
        poly = zooms[zoom]['base']
        #~ _ = os.path.join(mapper_gdb, os.path.basename(poly))
        def makeFinalPoly(_):
            env_push()
            arcpy.env.outputCoordinateSystem = None
            # don't use check_make since we already know we called it
            copyByFields(poly, _, FINAL_COLUMNS)
            env_pop()
            count = countRows(_)
            print('Processing {} rows'.format(count))
            i = 0
            next_break = 0
            print("Opening {} for update".format(_))
            with arcpy.da.UpdateCursor(_, FINAL_COLUMNS, sql_clause=['', "ORDER BY Id"]) as cursor:
                print("Opening {} for read".format(final_point))
                with arcpy.da.SearchCursor(final_point, FINAL_COLUMNS, sql_clause=['', "ORDER BY Id"]) as cur_point:
                    print("Updating...")
                    for row in cursor:
                        if i >= next_break:
                            cur_pct = int(i * 100.0 / count)
                            next_break = (cur_pct + 2) * count / 100
                            sys.stdout.write(str(cur_pct) if (0 == (cur_pct % 10)) else '.')
                        i += 1
                        row_point = cur_point.next()
                        for c in xrange(len(FINAL_COLUMNS)):
                            f = FINAL_COLUMNS[c]
                            if f == 'Id':
                                assert (row[c] == row_point[c]), "Point data is invalid: {}\n{}\n".format(str(row_point), str(row))
                            else:
                                row[c] = row_point[c]
                        cursor.updateRow(row)
                    print("100\nDone updating {} rows".format(i))
        final_poly = check_make(os.path.join(mapper_gdb, os.path.basename(poly)), makeFinalPoly)
    env_pop()
    # want to compress the final output too
    arcpy.Copy_management(mapper_gdb, _)
    #~ arcpy.CompressFileGeodatabaseData_management(_, "Lossless compression")
    arcpy.Compact_management(_)

import mapper
def updateService(fct, name, type='MapServer', folder='DSS'):
    fullName = name + "." + type
    try:
        mapper.stopServices(folder, fullName)
    except:
        pass
    try:
        fct()
        mapper.startServices(folder, fullName)
    except:
        pass


if __name__ == '__main__':
    if not arcpy.env.scratchWorkspace:
        arcpy.env.scratchWorkspace = arcpy.env.scratchGDB
    if not arcpy.env.workspace:
        arcpy.env.workspace = arcpy.env.scratchGDB
    print("Processing...")
    # \1
    env_push()
    env_defaults(workspace=POLY_GDB)
    # HACK: clear in case we were pasting this and it's set somehow
    arcpy.env.outputCoordinateSystem = None
    ntl_2018_reclassify = calc("ntl_2018", lambda _: arcpy.gp.Reclassify_sa(Raster(ntl_2018), "Value", ';'.join(["{} {}".format(k, v) for k, v in dct_2018.iteritems()]), _, "DATA"))
    province_project = project(PROVINCE, os.path.join(BOUNDS_GDB, "PROVINCE_project"))
    DAMAGE = check_make("damage", makeDamage)
    # /1
    env_pop()
    gridSize = CELLSIZE_M
    bigGridSize_km = 50
    bigGridSize_m = bigGridSize_km * 1000
    make_grid(ZONES)
    # \1
    bounds_grids = checkGDB(BOUNDS_DIR, "bounds_{:03d}m.gdb".format(CELLSIZE_M))
    env_push()
    env_defaults(workspace=bounds_grids,
                 cellSize=CELLSIZE_M)
    boundBox = check_make("BoundBox", lambda _: arcpy.MinimumBoundingGeometry_management(province_project, _, "ENVELOPE"))
    roundBound = check_make("RoundBound", lambda _: arcpy.Buffer_analysis(boundBox, _, BUFF_DIST))
    # HACK: don't want rounded corners so do this again.
    bounds = check_make("bounds", lambda _: arcpy.MinimumBoundingGeometry_management(roundBound, _, "ENVELOPE"))
    buffer = check_make("buffer", lambda _: arcpy.FeatureToRaster_conversion(bounds, arcpy.ListFields(bounds)[0].name, _, CELLSIZE_M))
    # NOTE: make sure [bounds] is first so it uses projection from it
    all_bounds = check_make("AllBounds", lambda _: arcpy.Merge_management(';'.join([bounds] + map(lambda x: os.path.join(BOUNDS_DIR, "zone_{}".format(x).replace(".", "_"), "grids_{}m.gdb".format(CELLSIZE_M), "ZoneBuffer"), ZONES)), _))
    DEM_BOX = check_make("box", lambda _: arcpy.MinimumBoundingGeometry_management(all_bounds, _, "ENVELOPE", "ALL"))
    # \2
    env_push()
    env_defaults(snapRaster=buffer, cellSize="")
    #~ PROVINCE_raster = calc("PROVINCE_raster", lambda _: arcpy.FeatureToRaster_conversion(province_project, "OBJECTID", _, CELLSIZE_M))
    DEM_clip = calc("DEM_clip", lambda _: clip_raster_box(EARTHENV, DEM_BOX, _), buildPyramids=False)
    DEM_project = calc("DEM_project", lambda _: project_raster(DEM_clip, _, cellsize_m=CELLSIZE_M, resampling_type="BILINEAR"))
    all_buffer = check_make("all_buffer", lambda _: arcpy.FeatureToRaster_conversion(DEM_BOX, arcpy.ListFields(DEM_BOX)[0].name, _, CELLSIZE_M))
    # /2
    env_pop()
    # \2
    env_push()
    env_defaults(mask=all_buffer, extent=all_buffer, snapRaster=all_buffer, cellSize="")
    # make a mask of what's in the country
    # make bounds for use in erasing from NHD data
    can_clip = check_make("canada_clip", lambda _: arcpy.Clip_analysis(canada, DEM_BOX, _))
    canada_project = project(can_clip, "canada_project")
    can_bounds = check_make("can_bounds", lambda _: arcpy.Merge_management(";".join([province_project, canada_project]), _))
    canada_box = check_make("canada_box", lambda _: arcpy.Clip_analysis(can_bounds, DEM_BOX, _))
    outside = check_make("outside", lambda _: arcpy.Erase_analysis(DEM_BOX, province_project, _))
    canada_raster = check_make("canada_raster", lambda _: arcpy.FeatureToRaster_conversion(canada_box, "OBJECTID", _, CELLSIZE_M))
    # \3
    env_push()
    env_defaults(workspace=checkGDB(WATER_DIR, "water.gdb"))
    water_projected = checkGDB(WATER_DIR, "water_projected.gdb")
    def check_water(_):
        # \4
        env_push()
        env_defaults(extent=province_project, mask=province_project)
        # we use the water polygons to repopulate the rasters
        water_ON = makeWater('ON', water_projected, outside, orig=os.path.join(NDD_NON, "OHN_WATERBODY"))
        # /4
        env_pop()
        water_list = (['water_ON'] +
                     map(lambda _: makeWater(_, water_projected, province_project), ['MB', 'NU', 'NS', 'NB', 'QC']) +
                     [makeWater('US', water_projected, can_bounds, orig=lakes_nhd, clear=True, sql="FTYPE NOT IN ( 361, 378, 466 )", clip=DEM_BOX),
                      makeWater('USArea', water_projected, can_bounds, orig=lakes_nhd_area)])
        water_ALL = check_make("water_ALL", lambda _: arcpy.Merge_management(";".join(water_list), _))
        def makeWaterFinal(_):
            arcpy.Sort_management(water_ALL, _, [["Shape", "ASCENDING"]])
            arcpy.AddField_management(_, "gridcode", "SHORT")
            arcpy.CalculateField_management(_, "gridcode", "102", "PYTHON")
        return check_make(_, makeWaterFinal)
    WATER = check_make(os.path.join(water_projected, "water"), check_water)
    # /3
    env_pop()
    if DO_COPY_TO_SERVER or not DO_MAPPER:
        # separate these since they don't depend on each other
        fuels = map(create_fuel, ZONES)
    # /2
    env_pop()
    # /1
    env_pop()
    MAPPER_FINAL = os.path.join(GENERATED, "FuelGrid_FBP.gdb")
    if DO_MAPPER:
        check_make(MAPPER_FINAL, fixMapper)
    if DO_COPY_TO_SERVER:
        updateService(lambda: map(copy_to_server, fuels), 'FBP_UTM')
        def copyEFRI(_):
            orig = _
            zonename = orig[-4:]
            efri = orig.replace(r'fuel_100m.gdb\fuel_{}'.format(zonename),
                                 r'7_fuel\zone_{}\fuel_100m.gdb\fuel_efri_only'.format(zonename))
            copy_to_server(efri, 'fuel_{}'.format(zonename), workspace=r'data\DSS\Fuels_efri_only.gdb')
            return efri
        updateService(lambda: map(copyEFRI, fuels), 'eFRI_UTM')
        updateService(lambda: copy_to_server(ntl_2018_reclassify), 'ntl_2018')
        env_push()
        #~ updateService(lambda: copy_to_server(os.path.join(), 'fuel'), 'fuel')
        env_defaults(workspace=checkGDB(os.path.join(GENERATED, "lambert"), "fuel_{}m.gdb".format(gridSize)),
                     cellSize=CELLSIZE_M)
        #~ arcpy.env.outputCoordinateSystem = PROJECTION
        if DO_MAPPER:
            # update the whole database
            updateService(lambda: copy_to_server(MAPPER_FINAL, workspace=r'data\AFFES_Mapper5\Data'), 'mapperFuel')
        else:
            # just do the one raster
            updateService(lambda: copy_to_server(os.path.join(MAPPER_FINAL, "fuel_{}".format(CELLSIZE_M))), 'fuel')
        #~ updateService(lambda: copy_to_server("fuel_efri"), 'fuel_efri')
        #~ updateService(lambda: copy_to_server("fuel_filled"), 'fuel_filled')
        env_pop()
    print("Done")
