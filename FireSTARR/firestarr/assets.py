"""Generate assets list"""
from __future__ import print_function

import arcpy
import arcpy.da
import arcpy.sa
arcpy.CheckOutExtension("spatial")

import math
import os
import sys

import pandas as pd

from arc_util import parseExtent
from shared import env_pop
from shared import env_push
from shared import project
from shared import project_raster
from utm import lat_lon_to_utm
from utm import utm_to_lat_lon
from util import ensure_dir
from Settings import Settings

## Base folder to use for RamPART feature classes for assets list
RAMPART_BASE = os.path.join(Settings.HOME_DIR, r'..\data\GIS\generated\rampart')

def getZone(spatialReference):
    """!
    Determine UTM zone for given spatial reference
    @param spatialReference Spatial reference to determine zone from
    @return UTM zone represented by spatial reference
    """
    r = spatialReference.exporttostring()
    r = r[r.index('Central_Meridian'):]
    r = r[r.index(',') + 1:r.index(']') - 1]
    c = float(r)
    return (c + 183.0) / 6.0

def polygonFromExtent(x, spatialReference):
    """!
    Create a polygon that covers the given extent
    @param x Extent to cover
    @param spatialReference Spatial reference to use for polygon
    @return Polygon covering extent
    """
    array = arcpy.Array()
    array.add(arcpy.Point(x.XMax, x.YMax))
    array.add(arcpy.Point(x.XMax, x.YMin))
    array.add(arcpy.Point(x.XMin, x.YMin))
    array.add(arcpy.Point(x.XMin, x.YMax))
    return arcpy.Polygon(array, spatialReference)

def listLayers(df, wildcard):
    """!
    List layers in map document dataframe
    @param df DataFrame to list layers from
    @param wildcard Wildcard mask to match layers
    @return List of layers matching mask
    """
    return [x for x in arcpy.mapping.ListLayers(df, wildcard) if x.isFeatureLayer]

## Fields to look for to use for description of layer features
DESCRIPTION_FIELDS = [
    'LOCATION_DESCR',
    'BUILDING_TYPE',
    'FACILITY_TYPE',
    'Location',
    'TOWER_NAME',
    'FISHING_ACCESS_POINT_TYPE',
    'WELL_TYPE',
    'AIRPORT_TYPE',
    'PROTECTED_AREA_NAME_ENG',
    'FMU_NAME',
    'DESCR',
    'SITE_NAME',
]

def find_closest(x, y, fire_shape):
    """!
    Find closest point in feature to the given point
    @param x X coordinate
    @param y Y coordinate
    @param fire_shape Feature to find closest point of
    @return Closest point to (X, Y) that's part of fire_shape
    """
    dist = None
    angle = None
    closest = None
    if 1 == fire_shape.pointCount:
        return fire_shape.firstPoint
    for pts in fire_shape:
        for r in pts:
            #~ print(r)
            # sqrt doesn't matter since it's just relative size we care about
            if r:
                d = math.pow(abs(x - r.X), 2) + math.pow(abs(y - r.Y), 2)
                if dist is None or d < dist:
                    dist = d
                    closest = r
    return closest

def angleAndDistanceTo(x, y, fire_shape):
    """!
    Find angle and distance to closest point in feature to the given point
    @param x X coordinate
    @param y Y coordinate
    @param fire_shape Feature to find closest point of
    @return Angle from (X, Y) to closest point that's part of fire_shape
    @return Distance from (X, Y) to closest point that's part of fire_shape (m)
    """
    shp = arcpy.PointGeometry(arcpy.Point(x, y), fire_shape.spatialReference)
    closest = find_closest(x, y, fire_shape)
    ang = arcpy.PointGeometry(closest, shp.spatialReference).angleAndDistanceTo(shp)
    dist = ang[1]
    angle = ang[0] % 360
    return angle, dist
    #~ return 0, math.sqrt(dist)

def angleToDirection(deg):
    """!
    Convert angle in degrees to direction string
    @param deg Angle (degrees)
    @return Direction of angle (N is 0, E is 90, etc.)
    """
    return ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"][int(round(deg/22.5)) % 16]

def summarize(run_output, extent, spatialReference):
    """!
    Summarize assets that are withing the given extent
    @param run_output Folder with simulation outputs
    @param extent Extent to find assets in
    @param spatialReference Spatial reference to use
    @return pandas dataframe with assets list
    """
    arcpy.env.overwriteOutput = True
    arcpy.env.addOutputsToMap = True
    zone = getZone(spatialReference)
    zone_suffix = "_{}".format(zone).replace('.', '_')
    gdb_point = os.path.join(RAMPART_BASE, "points_100m{}.gdb".format(zone_suffix))
    gdb_poly = os.path.join(RAMPART_BASE, "polygons_100m{}.gdb".format(zone_suffix))
    fire = os.path.basename(os.path.dirname(run_output))
    arcpy.env.workspace = arcpy.GetSystemEnvironment('TEMP')
    arcpy.env.workspace = ensure_dir(os.path.join(arcpy.GetSystemEnvironment('TEMP'), arcpy.CreateUniqueName(fire)))
    vectors = {}
    for_points = []
    for_polygons = []
    print(extent.XMin, extent.XMax, extent.YMin, extent.YMax)
    prob = [x for x in os.listdir(run_output) if x.startswith('wxshield') and x.endswith('.asc')][-1]
    prob = os.path.join(run_output, prob)
    prob_raster = arcpy.sa.Raster(prob)
    #~ prob_int = arcpy.sa.Int(prob_raster * 1000)
    arcpy.env.extent = extent
    prob_zero = arcpy.sa.Con(arcpy.sa.IsNull(prob_raster), 0, prob_raster)
    fire_shape = None
    try:
        perim = [x for x in os.listdir(run_output) if x.startswith(fire) and x.endswith('{}.shp'.format(zone_suffix))][-1]
        perim = os.path.join(run_output, perim)
        print(perim)
    except:
        # HACK: projecting the point is removing it for some reason??
        perim = os.path.join(run_output, fire + '.shp')
    def do_summarize(gdb, fire_shape):
        env_push()
        arcpy.env.workspace = gdb
        features = map(lambda x: os.path.join(gdb, x), arcpy.ListFeatureClasses('*_proj'))
        env_pop()
        env_push()
        for input in features:
            added = 0
            name = os.path.basename(input).replace('{}_proj'.format(zone_suffix), '').replace('_', ' ').replace(' 100m', '').capitalize()
            print(name)
            arcpy.Clip_analysis(input, "in_memory\\extent", "in_memory\\clipped")
            arcpy.MakeFeatureLayer_management("in_memory\\clipped", "from_lyr")
            if 0 == int(arcpy.GetCount_management('from_lyr').getOutput(0)):
                #~ print("No results")
                continue
            lyr = "from_lyr"
            join_worked = False
            all_fields = [x.name for x in arcpy.Describe(input).fields]
            fields = ['SHAPE@']
            for f in DESCRIPTION_FIELDS:
                if f in all_fields:
                    fields.append(f)
                    break
            is_point = u'Point' == arcpy.Describe(input).shapeType
            sr = arcpy.Describe(input).spatialReference
            if fire_shape.spatialReference != sr:
                fire_shape = fire_shape.projectAs(sr)
            if is_point:
                arcpy.sa.ExtractValuesToPoints("from_lyr", prob, "in_memory\\probpts", "INTERPOLATE", "VALUE_ONLY")
                lyr = "in_memory\\probpts"
                fields.append('RASTERVALU')
            else:
                try:
                    oid = arcpy.Describe("from_lyr").oidFieldName
                    arcpy.sa.ZonalStatisticsAsTable('from_lyr',
                                                     oid,
                                                     prob_zero,
                                                     "in_memory\\stats",
                                                     "NODATA",
                                                     "MAXIMUM")
                    arcpy.AddJoin_management("from_lyr", oid, "in_memory\\stats", oid, "KEEP_ALL")
                    #~ if 0 < int(arcpy.GetCount_management("in_memory\\stats").getOutput(0)):
                    new_fields = []
                    for f in fields:
                        if f == 'SHAPE@':
                            new_fields.append(f)
                        else:
                            new_fields.append('clipped.' + f)
                    new_fields.append('stats.MAX')
                    fields = new_fields
                    #~ print("ZonalStatisticsAsTable worked")
                    join_worked = True
                except:
                    print("FAIL")
                    pass
            def addLayer(row):
                shp = row[0]
                pt = shp.firstPoint
                desc = "" if not row[1] else row[1].replace('\n', '').replace('\r', '')
                pr = None
                had_pr = False
                try:
                    pr = max(0, row[2])
                    pr = round(pr * 100, 1)
                    had_pr = True
                except:
                    pass
                if pr is None:
                    pr = 0.0
                    if not (is_point or join_worked):
                        print("Searching...")
                        for b in shp:
                            for g in b:
                                if g is not None:
                                    loc = "{} {}".format(g.X, g.Y)
                                    s = arcpy.GetCellValue_management(prob, loc).getOutput(0)
                                    if 'NoData' != s:
                                        pr = max(pr, float(s))
                if is_point:
                    lat, lon = utm_to_lat_lon(pt.X, pt.Y, zone, False)
                    z, x, y = lat_lon_to_utm(lat, lon)
                    r = [name, 'Point', desc, z, int(x), int(y), shp.firstPoint.X, shp.firstPoint.Y, pr, pr]
                    #~ print(r)
                    for_points.append(r)
                else:
                    c4 = None
                    if not fire_shape.disjoint(shp):
                        print("Looking")
                        if 1 == fire_shape.pointCount:
                            c4 = fire_shape.firstPoint
                        else:
                            for b in fire_shape:
                                for g in b:
                                    if shp.contains(g):
                                        c4 = g
                    if c4 is not None:
                        ang = [0, 0]
                    else:
                        #~ print("Finding closest")
                        c1 = find_closest(fire_shape.centroid.X, fire_shape.centroid.Y, shp)
                        c2 = find_closest(c1.X, c1.Y, fire_shape)
                        while True:
                            c3 = find_closest(c2.X, c2.Y, shp)
                            c4 = find_closest(c3.X, c3.Y, fire_shape)
                            if c1.X == c3.X and c1.Y == c3.Y and c2.X == c4.X and c2.Y == c4.Y:
                                break
                            c1 = c3
                            c2 = c4
                        ang = arcpy.PointGeometry(c3, fire_shape.spatialReference).angleAndDistanceTo(arcpy.PointGeometry(c4, fire_shape.spatialReference))
                    lat, lon = utm_to_lat_lon(c4.X, c4.Y, zone, False)
                    z, x, y = lat_lon_to_utm(lat, lon)
                    r = [name, 'Polygon', desc, z, int(x), int(y), c4.X, c4.Y, pr, pr, ang[0] % 360, ang[1]]
                    #~ print(r)
                    for_polygons.append(r)
            for row in arcpy.da.SearchCursor(lyr, fields):
                added += 1
                if (added % 1000) == 0:
                    print('.', end='')
                addLayer(row)
            if added > 1000:
                print('')
            print("Added {} entries".format(added))
            arcpy.Delete_management("from_lyr")
            arcpy.Delete_management("in_memory\\probpts")
        env_pop()
        return fire_shape
    p = polygonFromExtent(extent, arcpy.Describe(prob).spatialReference)
    arcpy.MakeFeatureLayer_management(p, "in_memory\\extent")
    cursor = arcpy.da.InsertCursor("in_memory\\extent", ['SHAPE@'])
    cursor.insertRow([p])
    del cursor
    for fire_row in arcpy.SearchCursor(perim):
        fire_shape = fire_row.Shape
    fire_shape = fire_shape.projectAs(arcpy.Describe(prob).spatialReference)
    fire_shape = do_summarize(gdb_point, fire_shape)
    fire_shape = do_summarize(gdb_poly, fire_shape)
    arcpy.Delete_management("in_memory\\extent")
    columns = ['Layer', 'Type', 'Zone', 'Basemap', 'Easting', 'Northing', 'Angle', 'Distance (m)', 'Avg %', 'Max %', 'Description']
    df = pd.DataFrame(for_points, columns=['Layer', 'Type', 'Description', 'Zone', 'Easting', 'Northing', 'X', 'Y', 'Avg %', 'Max %'])
    if len(df) > 0:
        df['Basemap'] = df.apply(lambda x: int(str(x['Easting'])[:2] + str(x['Northing'])[:3]), axis=1)
        df['KEY'] = df.apply(lambda x: x['Layer'] + str(x['Zone']) + str(x['Basemap']), axis=1)
        grouped = df.groupby(['Layer', 'Type', 'Zone', 'Basemap', 'KEY']).count()[['Description']].reset_index()
        formean = df.groupby(['Layer', 'Type', 'Zone', 'Basemap', 'KEY']).mean()
        bymean = formean[['Avg %']].reset_index()
        bymax = df.groupby(['Layer', 'Zone', 'Basemap', 'KEY']).max()[['Max %']].reset_index()
        byx = formean[['X']].reset_index()
        byy = formean[['Y']].reset_index()
        agg = pd.merge(grouped[grouped['Description'] > 3], bymean)
        agg = pd.merge(agg, bymax)
        agg = pd.merge(agg, byx)
        agg = pd.merge(agg, byy)
        singles = df[~df['KEY'].isin(agg['KEY'])]
        del agg['KEY']
        del singles['KEY']
        if len(agg) > 0:
            agg['Description'] = agg.apply(lambda x: str(x['Description']) + ' matches', axis=1)
            agg['Easting'] = ""
            agg['Northing'] = ""
            summary = pd.concat([singles, agg])
        else:
            summary = singles
        summary['Vector'] = summary.apply(lambda x: angleAndDistanceTo(x['X'], x['Y'], fire_shape), axis=1)
        summary['Angle'] = summary.apply(lambda x: x['Vector'][0], axis=1)
        summary['Distance (m)'] = summary.apply(lambda x: x['Vector'][1], axis=1)
        summary = summary[columns]
    else:
        summary = None
    df2 = pd.DataFrame(for_polygons, columns=['Layer', 'Type', 'Description', 'Zone', 'Easting', 'Northing', 'X', 'Y', 'Avg %', 'Max %', 'Angle', 'Distance (m)'])
    if len(df2) > 0:
        df2['Basemap'] = df2.apply(lambda x: int(str(x['Easting'])[:2] + str(x['Northing'])[:3]), axis=1)
        df2['KEY'] = df2.apply(lambda x: x['Layer'] + str(x['Zone']) + str(x['Basemap']), axis=1)
        grouped = df2.groupby(['Layer', 'Type', 'Zone', 'Basemap', 'KEY']).count()[['Description']].reset_index()
        formean = df2.groupby(['Layer', 'Type', 'Zone', 'Basemap', 'KEY']).mean()
        bymean = formean[['Avg %']].reset_index()
        bymax = df2.groupby(['Layer', 'Zone', 'Basemap', 'KEY']).max()[['Max %']].reset_index()
        byangle = formean[['Angle']].reset_index()
        bydistance = formean[['Distance (m)']].reset_index()
        agg = pd.merge(grouped[grouped['Description'] > 3], bymean)
        agg = pd.merge(agg, bymax)
        agg = pd.merge(agg, byangle)
        agg = pd.merge(agg, bydistance)
        singles = df2[~df2['KEY'].isin(agg['KEY'])]
        del agg['KEY']
        del singles['KEY']
        if len(agg) > 0:
            agg['Description'] = agg.apply(lambda x: str(x['Description']) + ' matches', axis=1)
            agg['Easting'] = ""
            agg['Northing'] = ""
            agg['X'] = ""
            agg['Y'] = ""
            summary2 = pd.concat([singles, agg])
        else:
            summary2 = singles
        summary2 = summary2[columns]
    if summary is not None and summary2 is not None:
        result = pd.concat([summary, summary2])
    elif summary is not None:
        result = summary
    elif summary2 is not None:
        result = summary2
    else:
        return None
    result['Direction'] = result.apply(lambda x: angleToDirection(x['Angle']) if x['Distance (m)'] > 0 else 'N/A', axis=1)
    result['Distance (m)'] = result.apply(lambda x: int(x['Distance (m)']), axis=1)
    result['Avg %'] = result.apply(lambda x: round(x['Avg %'], 1), axis=1)
    result['Max %'] = result.apply(lambda x: round(x['Max %'], 1), axis=1)
    result = result[[x if x != 'Angle' else 'Direction' for x in columns]]
    result = result.sort_values(['Distance (m)', 'Layer', 'Type', 'Basemap', 'Easting', 'Northing'])
    result = result.sort_values(['Max %'], ascending=False, kind='mergesort')
    return result

def doRun():
    """!
    Run for command line arguments
    @return None
    """
    i = int(sys.argv[1])
    run_output = sys.argv[2]
    fire = sys.argv[3]
    e = sys.argv[4]
    prefix = sys.argv[5]
    #~ run_output = r".\test\output\APK\APK005\2018-07-02_0935"
    #~ e = "443122.86805898 5061144.31958696 453663.889141021 5066732.33076298 NaN NaN NaN NaN"
    #~ run_output = r".\test\output\NOR\NOR072\2018-07-20_0000"
    #~ e = "498242.803905737 5229238.67263711 603653.01472615 5285118.78439733 NaN NaN NaN NaN"
    #~ i = [x for x in os.listdir(run_output) if x.startswith('intensity_H') and x.endswith('.asc')][0]
    probs = [x for x in os.listdir(run_output) if x.startswith(prefix) and x[-3:] == "asc"]
    prob = probs[i]
    #~ spatialReference = arcpy.Describe(os.path.join(run_output, i)).spatialReference
    extent = parseExtent(e)
    #~ extent = parseExtent(sys.argv[1])
    #~ df = summarize(run_output, extent, spatialReference)
    #~ if df is not None:
        #~ df.to_csv("TEMP.csv", index=False)
    df = summarize(run_output, extent, arcpy.Describe(os.path.join(run_output, prob)).spatialReference)
    if df is not None:
        df.to_csv(os.path.join(run_output, "{}_{}_assets.csv".format(fire, os.path.basename(run_output))), index=False)

if __name__ == "__main__":
    doRun()
