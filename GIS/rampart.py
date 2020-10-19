"""Create RamPART rasters and intermediary gdbs"""
from __future__ import print_function

## Output raster cell size (m)
CELLSIZE_M = 100
import pandas as pd
import random
import datetime
from collections import OrderedDict
# HACK: import this so that we don't get error on sys.stdout.flush()
import sys
from sys import stdout
import os

## Root directory for GIS scripts
HOME_DIR = os.path.dirname(os.path.realpath(__import__("__main__").__file__))
sys.path.append(HOME_DIR)
sys.path.append(os.path.join(HOME_DIR, 'fbp_convert'))
import shared
#~ reload(shared)
from shared import *
import fuelconversion
#~ reload(fuelconversion)
from util import ensure_dir
from FuelLookup import *
import pandas as pd
import numpy as np

## base directory for GIS data
GIS_BASE = ensure_dir(r'C:\FireGUARD\data\GIS')
## intermediate data that doesn't get used anywhere else
RAMPART_TMP = ensure_dir(os.path.join(GIS_BASE, 'intermediate', 'rampart'))
## generated data that gets used in FireGUARD
RAMPART_OUT = ensure_dir(os.path.join(GIS_BASE, 'generated', 'rampart'))
## file that defines what to generate scores for and how to do so
SCORES = os.path.join(HOME_DIR, 'scores.csv')

def find_min(start, extent_min):
    x = start
    for p in xrange(9):
        n = pow(10, 10 - p)
        while x + n < extent_min:
            x += n
    return x
def find_max(start, extent_max):
    x = start
    for p in xrange(9):
        n = pow(10, 10 - p)
        while x + n < extent_max:
            x += n
    x += CELLSIZE_M
    return x


def cut_utm(to_cut, template):
    def makeEmpty(_):
        # dissolve so we have more chance of finding larger rectangles
        try:
            arcpy.Dissolve_management(to_cut, _)
        except:
            arcpy.Copy_management(to_cut, _)
        del_what = [x.name for x in arcpy.Describe(_).fields if not x.required]
        try:
            arcpy.DeleteField_management(_, ';'.join(del_what))
        except:
            # do it manually if that fails
            for f in del_what:
                try:
                    arcpy.DeleteField_management(_, f)
                except:
                    pass
        return _
    def make_split(_):
        split = check_make(_, makeEmpty)
        rectangles = check_make(os.path.basename(to_cut).replace('_proj', '_rectangles'), makeEmpty)
        spatial_reference = arcpy.Describe(split).spatialReference
        def explode(poly):
            all = []
            if 1 < poly.partCount:
                for i in xrange(poly.partCount):
                    p = arcpy.Polygon(poly.getPart(i), spatial_reference)
                    if p.area > 0:
                        all.append(p)
            else:
                all.append(poly)
            return all
        row = None
        all = []
        with arcpy.da.UpdateCursor(split, ["SHAPE@", "OID@"]) as polygons:
            for row in polygons:
                all += explode(row[0])
                polygons.deleteRow()
        with arcpy.da.UpdateCursor(rectangles, ["SHAPE@", "OID@"]) as polygons:
            for row in polygons:
                polygons.deleteRow()
        count = len(all)
        edit = arcpy.da.Editor(os.path.dirname(split))
        edit.startEditing(False, False)
        # all polygons should be in memory now
        with arcpy.da.InsertCursor(split, ["SHAPE@"]) as insert_cursor:
            with arcpy.da.InsertCursor(rectangles, ["SHAPE@"]) as rect_cursor:
                done = 0
                done_area = 0.0
                total_area = 0.0
                start_time = datetime.datetime.now()
                for p in all:
                    total_area += p.area / 10000.0
                while len(all) > 0:
                    #~ print("Starting")
                    last = all.pop()
                    result = [last]
                    extent = last.extent
                    xmin = find_min(arcpy.Describe(template).extent.XMin, extent.XMin)
                    xmax = find_max(xmin, extent.XMax)
                    ymin = find_min(arcpy.Describe(template).extent.YMin, extent.YMin)
                    ymax = find_max(ymin, extent.YMax)
                    #~ print([xmin, xmax, ymin, ymax])
                    x_steps = int((xmax - xmin) / CELLSIZE_M) + 1
                    xmid = (x_steps / 2) * CELLSIZE_M + xmin
                    y_steps = int((ymax - ymin) / CELLSIZE_M) + 1
                    ymid = (y_steps / 2) * CELLSIZE_M + ymin
                    # xmin and ymin will always be <= extent
                    if not (xmid >= extent.XMax and ymid >= extent.YMax):
                        def make_extent(x1, y1, x2, y2):
                            if x1 != x2 and y1 != y2:
                                # don't want to make a line or point
                                return [arcpy.Extent(x1, y1, x2, y2)]
                            return []
                        result = []
                        quadrants = []
                        quadrants += make_extent(xmin, ymin, xmid, ymid)
                        quadrants += make_extent(xmin, ymid, xmid, ymax)
                        quadrants += make_extent(xmid, ymin, xmax, ymid)
                        quadrants += make_extent(xmid, ymid, xmax, ymax)
                        for q in quadrants:
                            #~ print(q.XMin, q.XMax, q.YMin, q.YMax)
                            p = last.clip(q)
                            if p.area > 0:
                                result += explode(p)
                    if len(result) == 1:
                        #~ print("Found")
                        poly = result.pop()
                        e = poly.extent
                        if poly.area == ((e.XMax - e.XMin) * (e.YMax - e.YMin)):
                            rect_cursor.insertRow([poly])
                        elif poly.area >= 10001:
                            insert_cursor.insertRow([poly])
                            print("\nBad area {}".format(poly.area))
                            sys.exit(-1)
                        elif poly.area > 0:
                            insert_cursor.insertRow([poly])
                            done += 1
                            done_area += poly.area / 10000.0
                    else:
                        for poly in result:
                            e = poly.extent
                            if poly.area == ((e.XMax - e.XMin) * (e.YMax - e.YMin)):
                                # this polygon is a square the full size of the extent
                                done += 1
                                done_area += poly.area / 10000.0
                                rect_cursor.insertRow([poly])
                            else:
                                all.append(poly)
                    cur_time = datetime.datetime.now()
                    delta = cur_time - start_time
                    fract_done = (done_area / total_area)
                    estimate = 0 if 0 == fract_done else int(delta.total_seconds() * (1 - fract_done) / fract_done)
                    print("\r{:5.1f}% done: {}/{} ha, {} elapsed, {} remaining          \r".format(
                        100 * fract_done,
                        int(done_area),
                        int(total_area),
                        datetime.timedelta(seconds=int(delta.total_seconds())),
                        datetime.timedelta(seconds=estimate)),
                        end='')
        print("\nSaving " + split)
        edit.stopEditing(True)
        return split
    return check_make(os.path.basename(to_cut).replace('_proj', '_split'), make_split)

def cut_lines(to_cut, template):
    def makeEmpty(_):
        try:
            arcpy.Dissolve_management(to_cut, _)
        except:
            arcpy.Copy_management(to_cut, _)
        del_what = [x.name for x in arcpy.Describe(_).fields if not x.required]
        try:
            arcpy.DeleteField_management(_, ';'.join(del_what))
        except:
            # do it manually if that fails
            for f in del_what:
                try:
                    arcpy.DeleteField_management(_, f)
                except:
                    pass
        return _
    def make_split(_):
        split = check_make(_, makeEmpty)
        spatial_reference = arcpy.Describe(split).spatialReference
        def explode(line):
            all = []
            if 1 < line.partCount:
                for i in xrange(line.partCount):
                    p = arcpy.Polyline(line.getPart(i), spatial_reference)
                    if p.length > 0:
                        all.append(p)
            else:
                all.append(line)
            return all
        row = None
        all = []
        with arcpy.da.UpdateCursor(split, ["SHAPE@", "OID@"]) as lines:
            for row in lines:
                all += explode(row[0])
                lines.deleteRow()
        count = len(all)
        edit = arcpy.da.Editor(os.path.dirname(split))
        edit.startEditing(False, False)
        # all polygons should be in memory now
        with arcpy.da.InsertCursor(split, ["SHAPE@"]) as insert_cursor:
            done = 0
            done_dist = 0.0
            total_dist = 0.0
            start_time = datetime.datetime.now()
            for p in all:
                total_dist += p.length / 1000
            while len(all) > 0:
                #~ print("Starting")
                last = all.pop()
                result = [last]
                extent = last.extent
                xmin = find_min(arcpy.Describe(template).extent.XMin, extent.XMin)
                xmax = find_max(xmin, extent.XMax)
                ymin = find_min(arcpy.Describe(template).extent.YMin, extent.YMin)
                ymax = find_max(ymin, extent.YMax)
                #~ print([xmin, xmax, ymin, ymax])
                x_steps = int((xmax - xmin) / CELLSIZE_M) + 1
                xmid = (x_steps / 2) * CELLSIZE_M + xmin
                y_steps = int((ymax - ymin) / CELLSIZE_M) + 1
                ymid = (y_steps / 2) * CELLSIZE_M + ymin
                # xmin and ymin will always be <= extent
                if not (xmid >= extent.XMax and ymid >= extent.YMax):
                    def make_extent(x1, y1, x2, y2):
                        if x1 != x2 and y1 != y2:
                            # don't want to make a line or point
                            return [arcpy.Extent(x1, y1, x2, y2)]
                        return []
                    result = []
                    quadrants = []
                    quadrants += make_extent(xmin, ymin, xmid, ymid)
                    quadrants += make_extent(xmin, ymid, xmid, ymax)
                    quadrants += make_extent(xmid, ymin, xmax, ymid)
                    quadrants += make_extent(xmid, ymid, xmax, ymax)
                    for q in quadrants:
                        #~ print(q.XMin, q.XMax, q.YMin, q.YMax)
                        p = last.clip(q)
                        if p.length > 0:
                            result += explode(p)
                if len(result) == 1:
                    #~ print("Found")
                    line = result.pop()
                    done_dist += line.length / 1000
                    insert_cursor.insertRow([line])
                else:
                    all += result
                cur_time = datetime.datetime.now()
                delta = cur_time - start_time
                fract_done = (done_dist / total_dist)
                estimate = 0 if 0 == fract_done else int(delta.total_seconds() * (1 - fract_done) / fract_done)
                print("\r{:5.1f}% done: {}/{} km, {} elapsed, {} remaining          \r".format(
                    100 * fract_done,
                    int(done_dist),
                    int(total_dist),
                    datetime.timedelta(seconds=int(delta.total_seconds())),
                    datetime.timedelta(seconds=estimate)),
                    end='')
        print("\nSaving " + split)
        edit.stopEditing(True)
        return split
    return check_make(os.path.basename(to_cut).replace('_proj', '_split'), make_split)



def makeRampart(zone_tif, grid, scores):
    suffix = os.path.splitext(os.path.basename(zone_tif))[0].replace('aspect', '')
    zone_suffix = suffix[:suffix.index('__')] if '__' in suffix else suffix
    gdb_out = checkGDB(os.path.join(RAMPART_OUT,
                                    "rampart{}.gdb".format(suffix)))
    proj_line = checkGDB(os.path.join(RAMPART_OUT,
                                     "lines{}.gdb".format(zone_suffix)))
    proj_poly = checkGDB(os.path.join(RAMPART_OUT,
                                     "polygons{}.gdb".format(zone_suffix)))
    proj_point = checkGDB(os.path.join(RAMPART_OUT,
                                     "points{}.gdb".format(zone_suffix)))
    gdb_line = checkGDB(os.path.join(RAMPART_TMP,
                                     "lines{}.gdb".format(zone_suffix)))
    gdb_poly = checkGDB(os.path.join(RAMPART_TMP,
                                     "polygons{}.gdb".format(zone_suffix)))
    gdb_point = checkGDB(os.path.join(RAMPART_TMP,
                                     "points{}.gdb".format(zone_suffix)))
    env_push()
    env_defaults(mask=zone_tif,
                 workspace=gdb_line,
                 snapAndExtent=zone_tif)
    arcpy.env.cellSize = zone_tif
    cellSize = int(arcpy.env.cellSize)
    area = cellSize * cellSize
    ref = arcpy.Describe(zone_tif).spatialReference
    ext = arcpy.Describe(zone_tif).extent
    lower_left = "{} {}".format(ext.lowerLeft.X, ext.lowerLeft.Y)
    align_left = "{} {}".format(ext.lowerLeft.X, ext.lowerLeft.Y + 10)
    upper_right = "{} {}".format(ext.upperRight.X, ext.upperRight.Y)
    def do_project(name, input, select_clause):
        from_lyr = input
        # if we didn't subset then everything is in there,
        # but if we did then this doesn't work for other areas
        proj_name = name + zone_suffix + "_proj"
        if select_clause:
            proj_name = name + suffix + "_proj"
            def mkSubset(_):
                arcpy.MakeFeatureLayer_management(input, "from_lyr", "", "in_memory")
                arcpy.SelectLayerByAttribute_management("from_lyr",
                                                        "NEW_SELECTION",
                                                        select_clause)
                arcpy.CopyFeatures_management("from_lyr", _)
                arcpy.Delete_management("from_lyr")
            from_lyr = check_make(os.path.basename(name) + suffix + "_subset", mkSubset)
        # want to clip to the grid no matter what
        from_lyr = check_make(os.path.basename(name) + suffix + "_clip",
                              lambda _: arcpy.Clip_analysis(from_lyr, grid, _))
        proj = project(from_lyr, proj_name, ref)
        return proj
    def project_and_cut(name, input, zone_tif, select_clause):
        split_name = name + zone_suffix + "_split"
        if not arcpy.Exists(split_name):
            proj = do_project(os.path.join(proj_poly, name), input, select_clause)
            intersect = cut_utm(proj, zone_tif)
            arcpy.RepairGeometry_management(intersect, "DELETE_NULL")
        return split_name
    for row in scores.iterrows():
        name = row[0]
        data = row[1]
        input = data['input']
        select_clause = data.query if (str == type(data.query) and 0 < len(data.query)) else None
        def process(_):
            def process_line(_):
                arcpy.env.workspace = gdb_line
                root = name + "_M" + suffix
                proj = do_project(os.path.join(proj_line, name), input, select_clause)
                count = int(arcpy.GetCount_management(proj)[0])
                if 0 == count:
                    #~ return calc(_, 
                                 #~ lambda _: arcpy.CreateRasterDataset_management(os.path.dirname(_),
                                                                                 #~ os.path.basename(_),
                                                                                 #~ CELLSIZE_M,
                                                                                 #~ "64_BIT",
                                                                                 #~ zone_tif,
                                                                                 #~ 1))
                     return calc(_,
                                  lambda _: SetNull(BooleanNot(IsNull(zone_tif)), zone_tif))
                intersect = cut_lines(proj, zone_tif)
                if 'AREA' not in [x.name for x in arcpy.Describe(intersect).fields]:
                    shp = arcpy.Describe(intersect).shapeFieldName
                    arcpy.AddField_management(intersect, "LENGTH", "DOUBLE")
                    arcpy.CalculateField_management(intersect,
                                                    "LENGTH",
                                                    "!{}.length@meters!".format(shp),
                                                    "PYTHON")
                    arcpy.AddField_management(intersect, "PRIORITY", "INTEGER")
                    arcpy.CalculateField_management(intersect, "PRIORITY", "1", "PYTHON")
                # if we find the centroid then it must be in the cell because everything else is
                points = check_make(root + "_points",
                                    lambda _: arcpy.FeatureVerticesToPoints_management(intersect,
                                                                                        _,
                                                                                        "MID"))
                raster = calc(root,
                                  lambda _: arcpy.PointToRaster_conversion(
                                                points,
                                               "LENGTH",
                                               _,
                                               "SUM",
                                               "PRIORITY",
                                               str(cellSize)))
                # output is per 1km
                return calc(_, lambda _: Con(IsNull(raster), raster, raster / 1000))
            def process_poly(_):
                arcpy.env.workspace = gdb_poly
                root = name + "_HA" + suffix
                intersect = project_and_cut(name, input, zone_tif, select_clause)
                if 'AREA' not in [x.name for x in arcpy.Describe(intersect).fields]:
                    print("Finding areas for " + name)
                    shp = arcpy.Describe(intersect).shapeFieldName
                    arcpy.AddField_management(intersect, "AREA", "DOUBLE")
                    arcpy.CalculateField_management(intersect,
                                                    "AREA",
                                                    "!{}.area@hectares!".format(shp),
                                                    "PYTHON")
                    # need a priority field so that cells with < 50% area are still counted
                    arcpy.AddField_management(intersect, "PRIORITY", "INTEGER")
                    arcpy.CalculateField_management(intersect, "PRIORITY", "1", "PYTHON")
                rectangles = intersect.replace('_split', '_rectangles')
                if 'AREA' not in [x.name for x in arcpy.Describe(rectangles).fields]:
                    arcpy.AddField_management(rectangles, "AREA", "DOUBLE")
                    # set area to be one cell in hectares
                    arcpy.CalculateField_management(rectangles, "AREA", area / 10000.0, "PYTHON")
                # need to set all cells that are covered by rectangles to be 100%
                full_cells = check_make(rectangles.replace('_rectangles', '_full'),
                                        lambda _: arcpy.PolygonToRaster_conversion(
                                                                         rectangles,
                                                                         "AREA",
                                                                         _,
                                                                         "CELL_CENTER"))
                # convert to points so we can use sum of areas
                points = check_make(root + "_points",
                                    lambda _: arcpy.FeatureToPoint_management(
                                                intersect,
                                                _,
                                                "INSIDE"))
                partial = calc(root + "_partial",
                              lambda _: arcpy.PointToRaster_conversion(
                                            points,
                                           "AREA",
                                           _,
                                           "SUM",
                                           "PRIORITY",
                                           str(cellSize)))
                # output is per 100ha
                per_100ha = 10000.0 / area * 100.0
                out = calc(_,
                           lambda _: Con(IsNull(partial), full_cells, partial) / per_100ha)
                return out
            def process_point(_):
                arcpy.env.workspace = gdb_point
                root = name + "_C" + suffix
                proj = do_project(os.path.join(proj_point, name), input, select_clause)
                root = check_make(root,
                                  lambda _: arcpy.PointToRaster_conversion(proj,
                                                                            "OBJECTID",
                                                                            _,
                                                                            "COUNT",
                                                                            "NONE",
                                                                            str(cellSize)))
                # output is straight count of points
                out = calc(_,
                           lambda _: arcpy.CopyRaster_management(root, _))
            shape_type = arcpy.Describe(input).shapeType
            if 'Point' == shape_type or 'Multipoint' == shape_type:
                return check_make(_, process_point)
            elif 'Polyline' == shape_type:
                return check_make(_, process_line)
            elif 'Polygon' == shape_type:
                return check_make(_, process_poly)
            else:
                print("Invalid type {} for {}".format(shape_type, name))
        out = check_make(os.path.join(gdb_out, name + suffix), process)
    env_pop()
    return gdb_out

scores = pd.read_csv(SCORES).set_index('key')
# for index,  row in scores.iterrows():
#     print(index)

categories = [x[:x.index('.')] for x in scores.columns if 'high' in x]
severities = sorted([x[x.index('.')+1:] for x in scores.columns if categories[0] in x])

ZONE = 14.5
if len(sys.argv) > 1:
    ZONE = float(sys.argv[1])

ZONE_STRING = str(ZONE).replace('.', '_')

zone_tif = os.path.join(GIS_BASE, r'generated\fuels\out_100m\aspect_100m_{}.TIF'.format(ZONE_STRING))
grid = os.path.join(GIS_BASE, r'intermediate\fuels\01_bounds\zone_{}\grids_100m.gdb\ZoneGrid'.format(ZONE_STRING))
gdb = makeRampart(zone_tif, grid, scores)
#~ FROM_FOLDER = os.path.join(GIS_BASE, r'generated\fuels\out_100m')
#~ tiles = [os.path.join(FROM_FOLDER, x) for x in os.listdir(FROM_FOLDER) if x.startswith('aspect_') and x.lower().endswith('.tif')]

#~ for zone_tif in tiles:
    #~ makeRampart(zone_tif)


RAMPART_SCORED = ensure_dir(os.path.join(RAMPART_OUT, "scored"))

scored_gdb = checkGDB(os.path.join(RAMPART_SCORED, os.path.basename(gdb)))

arcpy.env.workspace = gdb
rasters = arcpy.ListRasters('*')
#~ print(rasters)
suffix = os.path.splitext(os.path.basename(zone_tif))[0].replace('aspect', '')
zone_suffix = suffix[:suffix.index('__')] if '__' in suffix else suffix

by_key = OrderedDict()
for c in sorted(scores.index):
    #~ print("Looking for '{}{}'".format(c, suffix))
    by_key[c] = os.path.join(gdb, [x for x in rasters if x == '{}{}'.format(c, suffix)][0])

weights = {
    'affes': 0.42,
    'economic': 0.26,
    'social': 0.32,
}
for s in severities:
    def makeSumAll(_):
        sum_all = Int(Raster(zone_tif) * 0.0)
        # Divide by sum of economic and social so that they sum to 10 and affes can make it go over 10
        div_by = weights['economic'] + weights['social']
        for c in categories:
            cur_dir = ensure_dir(os.path.join(RAMPART_OUT, "scored", s))
            cur_gdb = checkGDB(os.path.join(cur_dir, '{}{}'.format(c, suffix)))
            for_this = scores[c + '.' + s]
            for index in by_key:
                value = for_this[index]
                if value and not np.isnan(value):
                    input = by_key[index]
                    scored = calc(os.path.join(cur_gdb, os.path.basename(input)),
                                  lambda _: Int(1000000 * Con(IsNull(Raster(input)), 0.0, Raster(input) * float(value))))
            def make_sum(_):
                arcpy.env.workspace = cur_gdb
                rasters = arcpy.ListRasters('*')
                #~ sum_raster = Con(IsNull(Raster(rasters[0])), 0.0, IsNull(Raster(rasters[0])) * 0.0)
                sum_raster = Int(Raster(zone_tif) * 0.0)
                for r in rasters:
                    sum_raster += Raster(r)
                sum_raster = SetNull(0 == sum_raster, sum_raster)
                sum_raster = Int(sum_raster)
                sum_raster.save(_)
            sum_raster = calc(os.path.join(scored_gdb, '{}_{}{}'.format(c, s, suffix)), make_sum)
            result = calc(os.path.join(RAMPART_OUT, sum_raster.name + '.tif'),
                          lambda _: arcpy.CopyRaster_management(sum_raster, _))
            sum_all = Int(sum_all + Con(IsNull(sum_raster), 0, sum_raster) * weights[c] / div_by)
        sum_all = Int(sum_all)
        sum_all = SetNull(0 == sum_all, sum_all)
        sum_all.save(_)
    sum_all = calc(os.path.join(RAMPART_OUT, 'weighted_{}{}.tif'.format(s, suffix)), makeSumAll)


MNR_LAMBERT = arcpy.SpatialReference('Projected Coordinate Systems/National Grids/Canada/NAD 1983 CSRS Ontario MNR Lambert')
arcpy.env.outputCoordinateSystem = MNR_LAMBERT
arcpy.env.workspace = ensure_dir(RAMPART_OUT)

def makeLambert(what):
    """Make Lambert Conformal Conic projected raster"""
    mask = ';'.join(arcpy.ListRasters('{}*'.format(what)))
    return check_make(os.path.join(RAMPART_OUT, '{}_100m_lambert.tif'.format(what)),
                       lambda _: arcpy.MosaicToNewRaster_management(
                                                mask,
                                                os.path.dirname(_),
                                                os.path.basename(_),
                                                MNR_LAMBERT,
                                                "32_BIT_UNSIGNED",
                                                100,
                                                1,
                                                "FIRST",
                                                "FIRST"))

#~ if 1 == len(sys.argv):
    #~ makeLambert('affes_high')
    #~ makeLambert('social_high')
    #~ makeLambert('economic_high')
    #~ makeLambert('weighted_high')

