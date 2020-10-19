"""Non-ArcGIS GIS utility code"""

import logging
import os
import sys

from osgeo import gdal, ogr, osr
import numpy as np

from Settings import Settings
from util import ensure_dir

def GetFeatureCount(shp):
    """!
    Count number of features in a shapefile
    @param shp Shapefile to count features from
    @return Number of features in shapefile, or -1 on failure
    """
    lyr = ogr.Open(shp)
    if lyr:
        return lyr.GetLayer(0).GetFeatureCount()
    return -1

def FromEPSG(epsg):
    """!
    Load spatial reference from epsg value
    @param epsg Code for spatial reference to load
    @return Spatial reference for given code
    """
    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromEPSG(epsg)
    return spatialReference

def Delete(shp):
    """!
    Delete the given shapefile
    @param shp Shapefile to delete
    @return None
    """
    if os.path.exists(shp):
        ogr.GetDriverByName('ESRI Shapefile').DeleteDataSource(shp)

def GetSpatialReference(src):
    """!
    Determine spatial reference from a source file
    @param src Source file to determine spatial reference of
    @return Spatial reference of source file
    """
    if src.endswith(".shp"):
        inDataSet = ogr.GetDriverByName('ESRI Shapefile').Open(src)
        inLayer = inDataSet.GetLayer()
        ref = inLayer.GetSpatialRef()
        del inLayer
        del inDataSet
        return ref
    inDataSet = gdal.Open(src)
    ref = inDataSet.GetProjectionRef()
    s = osr.SpatialReference()
    s.ImportFromWkt(ref)
    del ref
    del inDataSet
    return s

def Project(src, outputShapefile, outSpatialRef):
    """!
    Project to given spatial reference
    @param src File to project
    @param outputShapefile Destination file to save projection to
    @param outSpatialRef Spatial reference to project into
    @return None
    """
    # https://pcjericks.github.io/py-gdalogr-cookbook/projection.html
    # input SpatialReference
    # get the input layer
    inDataSet = ogr.GetDriverByName('ESRI Shapefile').Open(src)
    inLayer = inDataSet.GetLayer()
    # create the CoordinateTransformation
    inSpatialRef = GetSpatialReference(src)
    #~ print inSpatialRef.ExportToWkt()
    #~ print outSpatialRef.ExportToWkt()
    coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
    # create the output layer
    Delete(outputShapefile)
    outDataSet = ogr.GetDriverByName('ESRI Shapefile').CreateDataSource(outputShapefile)
    outLayer = outDataSet.CreateLayer(inLayer.GetName(), outSpatialRef, geom_type=ogr.wkbMultiPolygon)
    # add fields
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        if 'shape' not in fieldDefn.GetName().lower():
            outLayer.CreateField(fieldDefn)
    # get the output layer's feature definition
    outLayerDefn = outLayer.GetLayerDefn()
    # loop through the input features
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        # get the input geometry
        geom = inFeature.GetGeometryRef()
        # reproject the geometry
        geom.Transform(coordTrans)
        # create a new feature
        outFeature = ogr.Feature(outLayerDefn)
        # set the geometry and attribute
        outFeature.SetGeometry(geom)
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
        # add the feature to the shapefile
        outLayer.CreateFeature(outFeature)
        # dereference the features and get the next input feature
        del outFeature
        inFeature = inLayer.GetNextFeature()
    # Save and close the shapefiles
    del coordTrans
    del inSpatialRef
    del inLayer
    del inDataSet
    del inFeature
    del outLayerDefn
    del inLayerDefn
    del outLayer
    del outDataSet
    # create projection file for output
    prj = os.path.splitext(outputShapefile)[0] + ".prj"
    with open (prj, 'w') as file:
        file.write(outSpatialRef.ExportToWkt())

class Extent(object):
    """Represents the extent of a shapefile"""
    def __init__(self, src):
        """!
        Load from src
        @param self Pointer to this
        @param src Shapefile to load extent from
        """
        shp = ogr.GetDriverByName('ESRI Shapefile').Open(src)
        extent = shp.GetLayer().GetExtent()
        ## Minimum X coordinate
        self.XMin = extent[0]
        ## Maximum X coordinate
        self.XMax = extent[1]
        ## Center between minimum and maximum X coordinates
        self.XCenter = (self.XMax - self.XMin) / 2 + self.XMin
        ## Minimum Y coordinate
        self.YMin = extent[2]
        ## Maximum Y coordinate
        self.YMax = extent[3]
        ## Center between minimum and maximum Y coordinates
        self.YCenter = (self.YMax - self.YMin) / 2 + self.YMin

def GetCellSize(raster):
    """!
    Determine cell size for a raster and ensure pixels are square
    @param raster Raster to get cell size from
    @return Cell size for raster (m)
    """
    r = gdal.Open(raster, gdal.GA_ReadOnly)
    gt = r.GetGeoTransform()
    pixelSizeX = gt[1]
    pixelSizeY =-gt[5]
    if pixelSizeX != pixelSizeY:
        print "Raster must have square pixels"
        sys.exit(-2)
    del r
    del gt
    return pixelSizeX

def Rasterize(shp, raster, reference):
    """!
    Convert a shapefile into a raster with the given spatial reference
    @param shp Shapefile to convert to raster
    @param raster Raster file path to save result to
    @param reference Reference raster to use for extents and alignment
    @return None
    """
    # https://gis.stackexchange.com/questions/222394/how-to-convert-file-shp-to-tif-using-ogr-or-python-or-gdal/222395
    gdalformat = 'GTiff'
    datatype = gdal.GDT_Byte
    burnVal = 1 # value for the output image pixels
    # Get projection info from reference image
    ref_raster = gdal.Open(reference, gdal.GA_ReadOnly)
    gt = ref_raster.GetGeoTransform()
    pixelSizeX = gt[1]
    pixelSizeY =-gt[5]
    if pixelSizeX != pixelSizeY:
        print "Raster must have square pixels"
        sys.exit(-2)
    # Open Shapefile
    shapefile = ogr.Open(shp)
    shapefile_layer = shapefile.GetLayer()
    # Rasterise
    #~ print("Rasterising shapefile...")
    output = gdal.GetDriverByName(gdalformat).Create(raster, ref_raster.RasterXSize, ref_raster.RasterYSize, 1, datatype, options=['TFW=YES', 'COMPRESS=LZW', 'TILED=YES'])
    output.SetProjection(ref_raster.GetProjectionRef())
    output.SetGeoTransform(ref_raster.GetGeoTransform()) 
    # Write data to band 1
    band = output.GetRasterBand(1)
    band.SetNoDataValue(0)
    gdal.RasterizeLayer(output, [1], shapefile_layer, burn_values=[burnVal])
    # Close datasets
    del band
    del output
    del ref_raster
    del shapefile
    # create projection file for output
    prj = os.path.splitext(raster)[0] + ".prj"
    with open (prj, 'w') as file:
        file.write(GetSpatialReference(shp).ExportToWkt())

def save_point_shp(latitude, longitude, out_dir, name):
    """!
    Save a shapefile with a single point having the given coordinates
    @param latitude Latitude to use for point
    @param longitude Longitude to use for point
    @param out_dir Directory to save shapefile to
    @param name Name of point within file, and file to save to
    @return None
    """
    save_to = os.path.join(out_dir, "{}.shp".format(name))
    from shapely.geometry import Point, mapping
    from fiona import collection
    from fiona.crs import from_epsg
    schema = { 'geometry': 'Point', 'properties': { 'name': 'str' } }
    with collection(save_to, "w", "ESRI Shapefile", schema, crs=from_epsg(4269)) as output:
        point = Point(float(longitude), float(latitude))
        output.write({
            'properties': {
                'name': name
            },
            'geometry': mapping(point)
        })

def sum_raster(raster, band_number=1):
    """!
    Sum the value of all cells in a raster
    @param raster Raster to sum values for
    @param band_number Number of band to sum values of
    @return Result of summing raster
    """
    src = gdal.Open(raster)
    band = src.GetRasterBand(band_number)
    nodata = band.GetNoDataValue()
    r_array = np.array(band.ReadAsArray())
    r_array[r_array == nodata] = 0.0
    result = r_array.sum()
    del r_array
    del band
    del src
    return result

## Dictionary of meridians to the rasters they are for
MERIDIANS = None

def find_raster_meridians(year):
    """!
    Find the meridians of input rasters for the given year
    @param year Year to find raster meridians for
    @return Dictionary of meridians to raster with each meridian
    """
    global MERIDIANS
    if MERIDIANS:
        return MERIDIANS
    raster_root = Settings.RASTER_DIR
    default_root = os.path.join(raster_root, "default")
    raster_root = os.path.join(raster_root, str(year))
    if not os.path.isdir(raster_root):
        raster_root = default_root
    rasters = [os.path.join(raster_root, x) for x in os.listdir(raster_root) if x[-4:].lower() == '.tif' and -1 != x.find('fuel')]
    result = {}
    for r in rasters:
        raster = gdal.Open(r)
        prj = raster.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        result[srs.GetProjParm('CENTRAL_MERIDIAN')] = r
        del srs
        del prj
        del raster
    MERIDIANS = result
    if 0 == len(result):
        logging.error("Error: missing rasters in directory {}".format(raster_root))
    return result

def find_best_raster(lon, year):
    """!
    Find the raster with the closest meridian
    @param lon Longitude to look for closest raster for
    @param year Year to find raster for
    @return Raster with the closest meridian to the desired longitude
    """
    logging.debug("Looking for raster for longitude {}".format(lon))
    best = 9999
    m = find_raster_meridians(year)
    for i in m.keys():
        if (abs(best - lon) > abs(i - lon)):
            best = i
    return m[best]

def rasterize_perim(run_output, perim, year, name, raster=None):
    """!
    Convert a perimeter to a raster
    @param run_output Folder to save perimeter to
    @param perim Perimeter to convert to raster
    @param year Year to find reference raster for projection
    @param name Name of fire to use for file name
    @param raster Specific name of file name to output to
    @return Perimeter that was rasterized
    @return Path to raster output
    """
    prj = os.path.join(run_output, os.path.basename(perim).replace('.shp', '_NAD1983.shp'))
    ensure_dir(os.path.dirname(prj))
    ref_NAD83 = osr.SpatialReference()
    ref_NAD83.SetWellKnownGeogCS('NAD83')
    #~ try:
    Project(perim, prj, ref_NAD83)
    del ref_NAD83
    r = find_best_raster(Extent(prj).XCenter, year)
    prj_utm = os.path.join(run_output, os.path.basename(perim).replace('.shp', os.path.basename(r)[9:14] + '.shp'))
    Delete(prj_utm)
    zone = GetSpatialReference(r)
    Project(perim, prj_utm, zone)
    del zone
    cellsize = GetCellSize(r)
    size = 0.0
    dataSource = ogr.GetDriverByName('ESRI Shapefile').Open(prj_utm, gdal.GA_ReadOnly)
    layer = dataSource.GetLayer()
    for feature in layer:
        geom = feature.GetGeometryRef()
        area = geom.GetArea()
        size += area / (cellsize * cellsize)
        del geom
        del feature
    del layer
    del dataSource
    if size < 1:
        # this is less than one cell in area so don't use perimeter
        perim = None
        raster = None
    else:
        if not raster:
            raster = os.path.join(run_output, name + '.tif')
        Rasterize(prj_utm, raster, r)
    return perim, raster
    #~ except:
        #~ return None, None
