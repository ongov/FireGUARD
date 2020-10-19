import arceditor
import arcpy

import os

arcpy.env.overwriteOutput = True

NON_SENSITIVE = common.CONFIG.get('FireGUARD', 'gis_share') + common.CONFIG.get('FireGUARD', 'gis_non_sensitive')
PROVINCIAL = common.CONFIG.get('FireGUARD', 'gis_prov')

# Script arguments
#~ HOME_DIR = os.path.dirname(os.path.realpath(__import__("__main__").__file__))
HOME_DIR = r'C:\FireGUARD\GIS'
File_GDB_Path = os.path.realpath(os.path.join(HOME_DIR, r'..\data\GIS\generated'))
File_GDB_Name = r'simplified.gdb'
To_GDB = os.path.join(File_GDB_Path, File_GDB_Name)

print "Preparing {}".format(To_GDB)
if not arcpy.Exists(To_GDB):
    print "Creating {}".format(To_GDB)
    arcpy.CreateFileGDB_management(File_GDB_Path, File_GDB_Name, "CURRENT")

print "Copying..."

SIMPLIFY_FEATURES = map(lambda _: os.path.join(NON_SENSITIVE, _),
                        [
                            "WETLAND",
                            "OHN_100K_WATERBODY",
                            "INDIAN_RESERVE",
                            "PROV_PARK_REGULATED",
                            "CONSERVATION_RESERVE",
                        ])

NON_SENSITIVE_FEATURES = map(lambda _: os.path.join(NON_SENSITIVE, _),
                        [
                            "OHN_100K_WATERCOURSE",
                            "MNRF_ROAD_SEGMENT",
                            "ORN_SEGMENT_WITH_ADDRESS",
                            "UTILITY_LINE",
                            "ORWN_TRACK",
                            "TOURISM_ESTABLISHMENT_AREA",
                            "COTTAGE_RESIDENTIAL_SITE",
                            "UTILITY_SITE",
                            "FIRE_COMMUNICATIONS_TOWER",
                            "RECREATION_POINT",
                            "BOAT_CACHE_LOCATION",
                            "FISHING_ACCESS_POINT",
                            "TRAPPER_CABIN",
                            "BUILDING_AS_SYMBOL",
                            "CL_NON_FREEHOLD_DISPOSITION",
                            "AIRPORT_OFFICIAL",
                            "FIRE_RESPONSE_SECTOR",
                            "MNR_DISTRICT",
                        ])

PROVINCIAL_FEATURES = map(lambda _: os.path.join(PROVINCIAL, _),
                        [
                            "COMMUNITIES",
                            "CITIESMAJOR",
                            "PROVINCIAL_FIRE_BLOCKS",
                            "PROVINCIAL_FIRE_INDEX",
                        ])

def doSimplify(input):
    output = os.path.join(To_GDB, os.path.basename(input))
    print "{} => {}".format(input, output)
    if not arcpy.Exists(output):
        arcpy.SimplifyPolygon_cartography(input, output, "POINT_REMOVE", "10 Meters", "0 SquareMeters", "NO_CHECK", "NO_KEEP")

def doCopy(input):
    output = os.path.join(To_GDB, os.path.basename(input))
    print "{} => {}".format(input, output)
    if not arcpy.Exists(output):
        arcpy.FeatureClassToFeatureClass_conversion(input, To_GDB, os.path.basename(input), "", "", "")

for f in SIMPLIFY_FEATURES:
    doSimplify(f)

for f in NON_SENSITIVE_FEATURES:
    doCopy(f)

for f in PROVINCIAL_FEATURES:
    doCopy(f)

arcpy.CompressFileGeodatabaseData_management(To_GDB)

