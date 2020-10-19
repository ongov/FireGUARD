"""Unpack eFRI data so that it can be classified using FBP fuels conversion process"""

# NOTE: This needs to run in ArcMap or else it doesn't work for some reason

## Size to use for cells (m)
CELLSIZE_M = 100
print "Importing packages..."
import arcpy
import arcinfo
from arcpy.sa import *
import os
import re

# HACK: import this so that we don't get error on sys.stdout.flush()
import sys
from sys import stdout

print "Checking out extensions..."
arcpy.CheckOutExtension("spatial")

## Directory this is run from
HOME_DIR = r'C:\FireGUARD\GIS'
sys.path.append(HOME_DIR)

## Main directory for GIS files
GIS_DIR = r'C:\FireGUARD\data\GIS'
## Input directory for GIS files - save the .zip with all the LIO eFRI data into this folder
INPUT_DIR = os.path.join(GIS_DIR, r'input\LIO')
## Output directory for final data
OUT_DIR = os.path.join(GIS_DIR, r'intermediate\LIO')
import unpack
from unpack import check_zip

from util import find_dirs
from util import find_files
from util import ensure_dir
from shared import copy_to_server
from shared import env_push
from shared import env_pop
from shared import checkGDB
from shared import check_make
from shared import getFeatures
import shutil

def do_run():
    """Unpack eFRI data"""
    ## Lambert conformal conic projection
    MNR_LAMBERT = arcpy.SpatialReference('Projected Coordinate Systems/National Grids/Canada/NAD 1983 CSRS Ontario MNR Lambert')
    ## base file name for data
    BASE_NAME = r'eFRI'
    ## File types to input from
    FIND_MASK = '*.zip'
    if len(sys.argv) > 1:
        BASE_NAME = sys.argv[1]
    if len(sys.argv) > 2:
        FIND_MASK = sys.argv[2]
    ## Where to unzip input files to
    OUT_GDBS = os.path.join(OUT_DIR, r'{}_gdbs'.format(BASE_NAME))
    ## Where to unzip exterior files
    UNZIP_FIRST = os.path.join(OUT_DIR, BASE_NAME)
    ## Where to unzip nested zipped files
    UNZIP_SECOND = os.path.join(OUT_DIR, r'{}_1'.format(BASE_NAME))
    #
    check_zip(INPUT_DIR, '*', file_mask=FIND_MASK, output=UNZIP_FIRST)
    # make sure we unzip any zips that were in the zips
    check_zip(UNZIP_FIRST, '*', output=UNZIP_SECOND)
    gdbs = find_dirs(UNZIP_SECOND, '*.gdb')
    #
    roots = sorted(map(os.path.basename, gdbs))
    for i in xrange(len(roots)):
        if roots[i] in roots[i + 1:]:
            print 'Error: duplicate directory name - ' + roots[i]
            sys.exit(-1)
    #
    ensure_dir(OUT_GDBS)
    #
    def try_move(x, move_to):
        """Try to move and do nothing on failure"""
        try:
            shutil.move(x, move_to)
        except:
            # must have moved a parent directory already
            pass
    #
    map(lambda x: try_move(x, OUT_GDBS), gdbs)
    #
    OUT_ZIPS = os.path.join(OUT_DIR, r'{}_zips'.format(BASE_NAME))
    ensure_dir(OUT_ZIPS)
    zips = find_files(UNZIP_SECOND, '*.zip')
    map(lambda x: try_move(x, OUT_ZIPS), zips)
    #
    UNZIP_THIRD = os.path.join(OUT_DIR, r'{}_2'.format(BASE_NAME))
    check_zip(OUT_ZIPS, '*', output=UNZIP_THIRD)
    gdbs = find_dirs(UNZIP_THIRD, '*.gdb')
    map(lambda x: try_move(x, OUT_GDBS), gdbs)
    #
    arcpy.env.overwriteOutput = True
    arcpy.env.addOutputsToMap = False
    #
    #~ # only find gdbs that end in -2D or _2D since those are the ones we care about
    # missing WhiteRiver since it's '2D_FRI.gdb'
    #~ gdbs = find_dirs(OUT_GDBS, '*[_-]2D.gdb')
    #~ gdbs = find_dirs(OUT_GDBS, '*.gdb')
    # HACK: only use gdbs with > 2 characters in name so we omit the '2D' and '3D' duplicates of Algonquin
    gdbs = sorted(find_dirs(OUT_GDBS, '???*.gdb'))
    ## Directory to output to
    FINAL_DIR = ensure_dir(r'C:\FireGUARD\data\GIS\intermediate\fuels')
    ## GDB to output to
    OUT_GDB = checkGDB(FINAL_DIR, "{}_LIO.gdb".format(BASE_NAME))
    ## GDB to output shapefiles of simplified bounds to
    OUT_GDB_COVERAGE = checkGDB(FINAL_DIR, "{}_LIO_coverage.gdb".format(BASE_NAME))
    #
    def findName(ds):
        """Find simplified name to use for dataset"""
        name = ds.replace('-', '_')
        if name.endswith('_w'):
            name = name[:-2]
        ignore = ['eFRI', '2D', 'Final', 'FRI', 'Dataset', 'Block', 'forest', 'Forest', 'FOREST', 'PP', '_', 'Topology', 'SMLS']
        # remove all numbers
        ignore +=  map(str, list(xrange(10)))
        for r in ignore:
            name = name.replace(r, '')
        # HACK: fix known abbreviations
        names = {
            'GCF': 'GordonCosens',
            'CA': 'Caribou',
            'DRMatawin': 'DogRiverMatawin',
            'Hrst': 'Hearst',
            'MagpieThunderH': 'Magpie',
            'PANA': 'Pukaskwa',
            'ARF': 'AbitibiRiver',
            'BA': 'Bancroft'
        }
        if name in names.keys():
            name = names[name]
        if name.isupper():
            name = name.capitalize()
        name = name.replace('lake', 'Lake')
        return name
    #
    def copyForest(gdb):
        """Copy from gdb"""
        print "Processing " + str(gdb)
        arcpy.env.workspace = gdb
        gdb_name = os.path.basename(gdb)
        try:
            ds = arcpy.ListDatasets()[0]
        except:
            # this is an empty folder, so skip
            return None
        if gdb_name.startswith('pp_FRI_FIMv2'):
            name = findName(re.match('pp_FRI_FIMv2_[^_]*_', gdb_name).group(0).replace('pp_FRI_FIMv2', ''))
        else:
            name = findName(ds)
        # HACK: if name consists of only those things we replace then look at gdb name
        if 0 == len(name):
            name = findName(gdb_name.replace('.gdb', ''))
        def mkForest(_):
            arcpy.env.workspace = os.path.join(gdb, ds)
            feats = arcpy.ListFeatureClasses()
            # HACK: assume feature with most rows is the forest polygon
            counts = map(lambda x: int(arcpy.GetCount_management(x)[0]), feats)
            forest = feats[counts.index(max(counts))]
            arcpy.CopyFeatures_management(forest, _)
        forest = check_make(os.path.join(OUT_GDB, name), mkForest)
        # using the coverage from the gdb is giving us the WMU, not the area covered by the data
        outline = check_make(os.path.join(OUT_GDB_COVERAGE, name), lambda _: arcpy.Dissolve_management(forest, _, '#'))
        if 'name' not in map(lambda x: x.name, arcpy.ListFields(outline)):
            arcpy.AddField_management(outline, 'name', "TEXT")
            arcpy.CalculateField_management(outline, 'name', '"{}"'.format(name), 'PYTHON')
        return name
    #
    def mkAll(_):
        ## list of names after copying from gdbs
        out = [x for x in sorted(map(copyForest, gdbs)) if x is not None]
        arcpy.env.outputCoordinateSystem = MNR_LAMBERT
        ## Merge all outlines together to make total area covered shape
        arcpy.Merge_management(';'.join(out), _)
    env_push()
    arcpy.env.workspace = OUT_GDB_COVERAGE
    ALL = arcpy.MakeFeatureLayer_management(check_make('ALL', mkAll))
    env_pop()
    # this is for updated example map services on test gis server
    if BASE_NAME == 'eFRI':
        fri_status = arcpy.MakeFeatureLayer_management(os.path.join(os.path.join(GIS_DIR, r'input\fuels\LIO'), r'FRI_STATUS_FT.shp'))
        # copy to service if we're doing eFRI data
        copy_to_server(ALL, 'eFRIdata')
        copy_to_server(fri_status, 'eFRIplanned')
        arcpy.SelectLayerByLocation_management(fri_status, "HAVE_THEIR_CENTER_IN", ALL, invert_spatial_relationship="INVERT")
        # HACK: can't think of a better way to do this
        arcpy.SelectLayerByAttribute_management(fri_status, "REMOVE_FROM_SELECTION", "UNIT_NAME like '%Nipigon%'")
        copy_to_server(fri_status, 'eFRIplanned_select')

if __name__ == "__main__":
    do_run()
