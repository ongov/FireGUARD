"""Update ADDI grid from mapper data that was made with fixWater.py"""
from __future__ import print_function

## Cell size to use (m)
CELLSIZE_M = 100
import pandas as pd

# HACK: import this so that we don't get error on sys.stdout.flush()
import sys
from sys import stdout
import os

#~ HOME_DIR = os.path.dirname(os.path.realpath(__import__("__main__").__file__))
## Home directory for GIS scripts
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

import arcpy


#~ def find_name(code):
    #~ if 1 == code:
        #~ return 'C1'
    #~ if 2 == code:
        #~ return 'C2'
    #~ if 3 == code:
        #~ return 'C3'
    #~ if 4 == code:
        #~ return 'C4'
    #~ if 5 == code:
        #~ return 'C5'
    #~ if 6 == code:
        #~ return 'C6'
    #~ if 7 == code:
        #~ return 'C7'
    #~ if 13 == code:
        #~ return 'D1'
    #~ if 31 == code:
        #~ return 'O1'
    #~ if code >= 600 and code < 700:
        #~ return 'M1'
    #~ if code >= 900 and code < 1000:
        #~ return 'M3'
    #~ return 'Invalid'

## ADDI grid to update
ADDI = r'C:\arod\ADDI\Input\Grid\ADDI_GRID_PROV.shp'

## Rampart raster to update grid with
RAMPART = r'C:\FireGUARD\data\GIS\rampart\weighted_high_100m_lambert.tif'

## Directory to output to
OUT_DIR = ensure_dir(r'C:\FireGUARD\data\GIS\out\ADDI')
## GDB ot output to
OUT_GDB = checkGDB(OUT_DIR, 'ADDI.gdb')
## Raster with zonal statistics for rampart data based on ADDI grid cells
OUT = os.path.join(OUT_DIR, 'RAMPART.tif')

calc(OUT, lambda _: arcpy.gp.ZonalStatistics_sa(ADDI, "FID", RAMPART, _, "SUM", "DATA"))


## Simplified fuel type without modifiers
fuel_simple = r'C:\FireGUARD\data\GIS\fuels\mapper\mapper.gdb\fuel_simple'
## Percent conifer
fuel_pc = r'C:\FireGUARD\data\GIS\fuels\mapper\mapper.gdb\fuel_pc'
## Percent dead fir
fuel_pdf = r'C:\FireGUARD\data\GIS\fuels\mapper\mapper.gdb\fuel_pdf'
## Mask to use for fuel rasters
mask = os.path.join(OUT_GDB, 'fuel_{}')

## calculated simplified fuel type raster
simple = calc(mask.format('simple'), lambda _: arcpy.gp.ZonalStatistics_sa(ADDI, "FID", fuel_simple, _, "MAJORITY", "DATA"))
## calculated percent conifer raster
pc = calc(mask.format('pc'), lambda _: arcpy.gp.ZonalStatistics_sa(ADDI, "FID", fuel_pc, _, "MEAN", "DATA"))
## calculated percent dead fir raster
pdf = calc(mask.format('pdf'), lambda _: arcpy.gp.ZonalStatistics_sa(ADDI, "FID", fuel_pdf, _, "MEAN", "DATA"))
## percent conifer, rounded to 25%, 50%, or 75%
pc_rounded = calc(mask.format('pc_rounded'), lambda _: Con(IsNull(pc), pc, Con(pc <= 25, 25, Con(pc <= 50, 50, 75))))
## percent dead fir, rounded to 30%, 60%, or 100%
pdf_rounded = calc(mask.format('pdf_rounded'), lambda _: Con(IsNull(pdf), pdf, Con(pdf <= 30, 30, Con(pdf <= 60, 60, 100))))

## majority fuel type, with calculated modifier if applicable
fuel = calc(mask.format('final'), lambda _: Con(60 == simple, 600 + pc_rounded, Con(90 == simple, Con(pdf_rounded == 100, 995, pdf_rounded + 900), simple)))

# tif is way faster for some reason
## output final TIFF
fuel = calc(os.path.join(OUT_DIR, "FUEL.tif"), lambda _: arcpy.CopyRaster_management(fuel, _))

def mkPoint(_):
    """Make point feature class with rampart and fuel code attributes"""
    arcpy.FeatureToPoint_management(in_features=ADDI, out_feature_class=_, point_location="INSIDE")
    arcpy.gp.ExtractMultiValuesToPoints_sa(_,
                                            OUT + " RAMPART",
                                            "NONE")
    arcpy.gp.ExtractMultiValuesToPoints_sa(_,
                                            os.path.join(fuel.path, fuel.name) + " FBP_CODE",
                                            "NONE")
    return _

## Point feature class based on ADDI grid inside points that has fuel and rampart values
ADDI_POINT = check_make(os.path.join(OUT_DIR, 'ADDI_point.shp'), mkPoint)

def mkPolygon(_):
    """Make updated polygon grid for ADDI"""
    arcpy.Copy_management(ADDI, _)
    arcpy.JoinField_management(in_data=_, in_field="INDEXVAL", join_table=ADDI_POINT, join_field="INDEXVAL", fields="RAMPART;FBP_CODE")
    remove = ['C1PERC', 'C2PERC', 'C3PERC', 'C4PERC', 'C5PERC', 'C6PERC', 'D1PERC', 'M1PERC', 'M3PERC', 'O1PERC', 'S1PERC']
    #arcpy.DeleteField_management(_, ';'.join(remove))
    # don't remove these because the code relies on column index by number
    for r in remove:
        arcpy.CalculateField_management(_, r, '-1', 'PYTHON')
    arcpy.CalculateField_management(in_table=_, field="FBP", expression="find_name(!FBP_CODE!)", expression_type="PYTHON", code_block="def find_name(code):\n    if 1 == code:\n        return 'C1'\n    if 2 == code:\n        return 'C2'\n    if 3 == code:\n        return 'C3'\n    if 4 == code:\n        return 'C4'\n    if 5 == code:\n        return 'C5'\n    if 6 == code:\n        return 'C6'\n    if 7 == code:\n        return 'C7'\n    if 13 == code:\n        return 'D1'\n    if 31 == code:\n        return 'O1'\n    if code >= 600 and code < 700:\n        return 'M1'\n    if code >= 900 and code < 1000:\n        return 'M3'\n    return 'Invalid'\n")
    # make rampart score based on density but then as if area were for a full 20km cell
    # NOTE: REMOVE THE MULTIPLICATION by 40,000 next year and change the symbology to use the same as firestarr
    arcpy.CalculateField_management(_, 'T_V_CELL', '!RAMPART! / !AREA! * 40000', 'PYTHON')
    arcpy.DeleteField_management(_, ';'.join(['FBP_CODE', 'RAMPART']))

## Updated polygon grid
addi = check_make(os.path.join(OUT_DIR, "ADDI_GRID_PROV.shp"), mkPolygon)
