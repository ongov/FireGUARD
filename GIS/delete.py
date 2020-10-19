"""Allow command line call to delete layers"""

import sys
import arcpy

for what in sys.argv[1:]:
    print "Deleting '{}'".format(what)
    arcpy.Delete_management(what)
