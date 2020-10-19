"""Saves a pdf and a png from a given mxd"""
import arcpy
import os
import sys

def saveBothMXD(mxd_path, mxd, destination):
    """!
    Save a pdf and a png from a given mxd
    @param mxd_path Path of mxd that is open
    @param mxd arcpy.mapping.MapDocument for the path
    @param destination PNG file to save to
    @return List with PNG file that was saved as single value
    """
    #~ print destination
    if os.path.exists(destination):
        os.remove(destination)
    arcpy.mapping.ExportToPNG(mxd, destination, resolution=75)
    destination_pdf = os.path.splitext(destination)[0] + ".pdf"
    #~ print destination_pdf
    if os.path.exists(destination_pdf):
        os.remove(destination_pdf)
    arcpy.mapping.ExportToPDF(mxd, destination_pdf, layers_attributes='NONE')
    return [destination]

def saveBoth(mxd_path, destination):
    """!
    Save a pdf and a png from a given mxd
    @param mxd_path Path of mxd that is open
    @param destination PNG file to save to
    @return List with PNG file that was saved as single value
    """
    return saveBothMXD(mxd_path, arcpy.mapping.MapDocument(mxd_path), destination)

if __name__ == '__main__':
    saveBoth(sys.argv[1], sys.argv[2])
