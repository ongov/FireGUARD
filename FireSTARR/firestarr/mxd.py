"""Make maps for everything"""
from __future__ import print_function

import math
import os
import shutil
import timeit

from dateutil.parser import parse

import pandas as pd
## HACK: disable warnings about this
pd.options.mode.chained_assignment = None

from log import *

from getFuelMXD import getFuelMXDName
from getImpactMXD import getImpactMXDName
from getProjectionMXD import getProjectionMXD
from getProjectionMXD import getProjectionMXDName
from getRiskMXD import getRiskMXDName
from getWxshield import getWxSHIELDFile
from PerimeterList import PerimeterList
from plotsize import makeSizeGraph
from Settings import Settings
from shared import env_pop
from shared import env_push
from shared import setSnapAndExtent
from util import ensure_dir
from util import find_date
from util import find_day
from util import find_line
from util import find_lines
from util import findSuffix
from util import finish_process
from util import fixK
from util import fixtime
from util import getMapOutput
from util import read_file
from util import readSimOutput
from util import start_process
from util import try_copy
from util import tryForceRemove
from util import write_file
from assets import summarize

logging.info("Importing arcpy...")
## Start time for loading arcpy
t0 = timeit.default_timer()
import arcpy
import arcpy.sa
arcpy.CheckOutExtension("spatial")
## End time for loading arcpy
t1 = timeit.default_timer()
logging.info("Took {}s to load arcpy".format(t1 - t0))

def makeMaps(scenario, run_output, force_maps, hide):
    """!
    @param scenario Scenario to use settings from
    @param run_output Folder where simulation output resides
    @param force_maps Whether or not to force making maps if they already exist
    @param hide Whether or not to show perimeter closest to date on map
    @return Path to final output pdf
    """
    import pdf
    from pdf import makePDF
    perimeters = PerimeterList(scenario.year, scenario.fire)
    sim_output = readSimOutput(run_output)
    startup = find_lines(sim_output, 'Startup indices ')
    startup = startup[0] if (len(startup) > 0) else "Startup indices are not valid"
    prefix = 'actuals_' if scenario.actuals_only else 'wxshield_'
    fire_prefix = scenario.fire + "_" + ('actual_' if scenario.actuals_only else '')
    probs = [x for x in os.listdir(os.path.join(Settings.HOME_DIR, run_output)) if x.startswith(prefix) and x[-3:] == "asc"]
    day0 =  find_day(probs[0]) - 1
    jds = map(find_day, probs)
    dates = map(find_date, probs)
    days = map(lambda x: x - day0, jds)
    extent = None
    perim = None
    ensure_dir(scenario.outbase)
    out_dir = os.path.join(scenario.outbase, scenario.fire[:3])
    ensure_dir(out_dir)
    for_time = os.path.basename(scenario.run_output)
    pdf_output = os.path.abspath(os.path.join(out_dir, fire_prefix + for_time + ".pdf"))
    copied = os.path.join(scenario.outbase, os.path.basename(pdf_output))
    # HACK: if any one map is required then make them all
    if not (force_maps or not os.path.exists(pdf_output)):
        logging.info("Maps already exist for " + scenario.fire)
        return copied
    for_time = os.path.basename(scenario.run_output)
    mapflag = os.path.join(out_dir, scenario.fire + "_" + for_time + "_mapsinprogress")
    if os.path.exists(mapflag):
        logging.info("Maps already being made for " + scenario.fire)
        return copied
    write_file(os.path.dirname(mapflag), os.path.basename(mapflag), " ")
    map_output = getMapOutput(run_output)
    logging.info("Making maps for " + scenario.fire)
    # HACK: run in parallel but assume this works for now
    wxshield = getWxSHIELDFile(dates[0], scenario.fire, map_output)
    processes = []
    run_what = r'python.exe firestarr\getWxshield.py {} {} {} {} {} "{}"'.format(scenario.lat, scenario.lon, dates[0], days[-1], scenario.fire, map_output)
    if 'overridden' in startup:
        startup_values = map(lambda x: x.strip(), startup[startup.find('(') + 1:-1].split(','))
        logging.debug(startup_values)
        # HACK: just use known positions for now
        #~ (0.0mm, FFMC 92.0, DMC 59.0, DC 318.0)
        #~ print(startup_values[0][:-2], startup_values[1][5:].strip(), startup_values[2][4:].strip(), startup_values[0][3:].strip())
        apcp = float(startup_values[0][:-2])
        ffmc = float(startup_values[1][5:].strip())
        dmc = float(startup_values[2][4:].strip())
        dc = float(startup_values[3][3:].strip())
        run_what += ' --apcp_0800 {} --ffmc {} --dmc {} --dc {}'.format(apcp, ffmc, dmc, dc)
    logging.debug(run_what)
    processes.append(start_process(run_what, Settings.PROCESS_FLAGS, Settings.HOME_DIR))
    arcpy.env.overwriteOutput = True
    ensure_dir(os.path.dirname(out_dir))
    ensure_dir(out_dir)
    # keep these until the end so they lock the file names
    mxd_paths = []
    mxd_names = []
    risk_paths = []
    risk_names = []
    scores = []
    txtFuelRaster = find_line(sim_output, 'Fuel raster is ', 'Fuel raster is ')
    suffix = findSuffix(txtFuelRaster)
    env_push()
    png_processes = []
    arcpy.env.scratchWorkspace = ensure_dir(arcpy.CreateScratchName(scenario.fire + os.path.basename(run_output),
                                                                    "",
                                                                    "Workspace",
                                                                    arcpy.GetSystemEnvironment('TEMP')))
    for i in reversed(xrange(len(days))):
        f = os.path.join(run_output, probs[i].replace(prefix, 'sizes_').replace('.asc', '.csv'))
        run_what = r'python.exe firestarr\plotsize.py "{}" "{}"'.format(f, days[i])
        png_processes = [start_process(run_what, Settings.PROCESS_FLAGS, Settings.HOME_DIR)] + png_processes
    for i in reversed(xrange(len(days))):
        finish_process(png_processes[i])
        arcpy.env.addOutputsToMap = False
        prob_input = os.path.join(run_output, probs[i])
        c_prob = arcpy.sa.Int(arcpy.sa.Raster(prob_input) * 10)
        shp_class = os.path.join(map_output, probs[i].replace(".asc", "_class_poly.shp").replace("-", "_"))
        # keep getting 'WARNING: Error of opening hash table for code page.' when we save to file plan
        poly = "in_memory\poly"
        logging.debug("Converting to polygon")
        arcpy.RasterToPolygon_conversion(c_prob, poly, "SIMPLIFY")
        del c_prob
        #~ print(shp_class)
        arcpy.CopyFeatures_management(poly, shp_class)
        del poly
        perim = None if hide else perimeters.find_perim(scenario.fire, dates[i])
        copyMXD = None
        if len(days) - 1 == i:
            # we need to get the extent from the last map
            copyMXD, theMXD, extent = getProjectionMXD(i, scenario.actuals_only, scenario.run_output, scenario.fire, extent, perim)
            run_what = r'python.exe firestarr\saveboth.py "{}" "{}"'.format(copyMXD, fire_prefix + dates[i] + ".png")
            processes.append(start_process(run_what, Settings.PROCESS_FLAGS, Settings.HOME_DIR))
            del theMXD
            run_what = r'python.exe firestarr\assets.py {} "{}" {} "{}" {}'.format(i, scenario.run_output, scenario.fire, extent, prefix)
        else:
            copyMXD = getProjectionMXDName(i, scenario.actuals_only, scenario.run_output, scenario.fire, extent, perim)
            run_what = r'python.exe firestarr\getProjectionMXD.py {} "{}" {} "{}"'.format(i, scenario.run_output, scenario.fire, extent)
            if scenario.actuals_only:
                run_what += ' --actuals'
            if perim:
                run_what += ' --perim "{}"'.format(perim)
        processes.append(start_process(run_what, Settings.PROCESS_FLAGS, Settings.HOME_DIR))
        mxd_paths = [copyMXD] + mxd_paths
        mxd_names = [fire_prefix + dates[i] + ".png"] + mxd_names
        start_raster = os.path.join(run_output, scenario.fire + '.tif')
        fire_raster = None
        if os.path.exists(start_raster):
            fire_raster = arcpy.sa.Raster(start_raster)
        # need to make sure the extent is the same for all rasters or they don't add properly
        env_push()
        setSnapAndExtent(prob_input)
        def by_intensity(intensity):
            letter = intensity.upper()[0]
            prob_i = os.path.join(run_output, prob_input.replace(prefix, 'intensity_{}_'.format(letter)))
            ra = Settings.RAMPART_MASK.format(intensity, suffix)
            logging.debug(prob_i)
            raster = arcpy.sa.Int(arcpy.sa.Raster(prob_i) * arcpy.sa.Raster(ra))
            if fire_raster is not None:
                # don't count anything in the starting perimeter
                # HACK: will not consider fires that start from just a size
                raster = arcpy.sa.Con(arcpy.sa.IsNull(fire_raster), raster, 0)
            raster = arcpy.sa.Con(arcpy.sa.IsNull(raster), 0, raster)
            return raster
        low_raster = by_intensity('low')
        moderate_raster = by_intensity('moderate')
        high_raster = by_intensity('high')
        total_raster = low_raster + moderate_raster + high_raster
        total_raster = arcpy.sa.SetNull(0 == total_raster, total_raster)
        total_path = os.path.join(map_output, prob_input.replace(prefix, 'RA_').replace('.asc', '.tif'))
        total_raster.save(total_path)
        del low_raster
        del moderate_raster
        del high_raster
        score = arcpy.RasterToNumPyArray(total_raster, nodata_to_value=0).sum()
        # .58 so that 10 for social & economic gives a 10 total score
        score = fixK(score / 1000000.0 / 0.58)
        env_pop()
        run_what = r'python.exe firestarr\getRiskMXD.py {} "{}" {} "{}" "{}"'.format(i, scenario.run_output, scenario.fire, extent, score)
        if scenario.actuals_only:
            run_what += ' --actuals'
        if perim:
            run_what += ' --perim "{}"'.format(perim)
        processes.append(start_process(run_what, Settings.PROCESS_FLAGS, Settings.HOME_DIR))
        copyMXD = getRiskMXDName(i, scenario.actuals_only, scenario.run_output, scenario.fire, extent, perim)
        risk_paths = [copyMXD] + risk_paths
        risk_names = [os.path.join(os.path.dirname(copyMXD), fire_prefix + dates[i] + "_risk.png")] + risk_names
        scores = [score] + scores
    env_pop()
    copyMXD = getFuelMXDName(fire_prefix, scenario.run_output, scenario.fire, extent, perim)
    run_what = r'python.exe firestarr\getFuelMXD.py {} "{}" {} "{}"'.format(fire_prefix, scenario.run_output, scenario.fire, extent)
    if perim:
        run_what += ' --perim "{}"'.format(perim)
    processes.append(start_process(run_what, Settings.PROCESS_FLAGS, Settings.HOME_DIR))
    mxd_paths = [copyMXD] + mxd_paths
    mxd_names = [fire_prefix + "_fuels.png"] + mxd_names
    mxd_names = map(lambda x: os.path.abspath(os.path.join(map_output, x)), mxd_names)
    copyMXD = getImpactMXDName(fire_prefix, scenario.run_output, scenario.fire, extent, perim)
    run_what = r'python.exe firestarr\getImpactMXD.py {} "{}" {} "{}"'.format(fire_prefix, scenario.run_output, scenario.fire, extent)
    if perim:
        run_what += ' --perim "{}"'.format(perim)
    processes.append(start_process(run_what, Settings.PROCESS_FLAGS, Settings.HOME_DIR))
    risk_paths = [copyMXD] + risk_paths
    risk_names = [os.path.join(os.path.dirname(copyMXD), fire_prefix + "_impact.png")] + risk_names
    for process in processes:
        finish_process(process)
    # HACK: put in not generated images for any missing maps
    if len(mxd_names) < 6:
        mxd_names = (mxd_names + [os.path.join(Settings.HOME_DIR, 'not_generated.png')] * 6)[:6]
    if len(risk_names) < 6:
        risk_names = (risk_names + [os.path.join(Settings.HOME_DIR, 'not_generated.png')] * 6)[:6]
    logging.debug(mxd_names + [wxshield] + risk_names)
    makePDF(scenario.fire, days, dates, mxd_names, wxshield, risk_names, sim_output, pdf_output, scores)
    try_copy(pdf_output, copied)
    # HACK: use known file name for assets
    csv_orig = os.path.abspath(os.path.join(run_output, fire_prefix + for_time + "_assets.csv"))
    csv_output = os.path.abspath(os.path.join(out_dir, os.path.basename(csv_orig)))
    csv_copied = os.path.join(scenario.outbase, os.path.basename(csv_orig))
    try_copy(csv_orig, csv_output)
    try_copy(csv_orig, csv_copied)
    fixtime(scenario.fire, parse(for_time.replace('_', ' ')),
                                 [pdf_output, copied, csv_orig, csv_copied])
    try:
        tryForceRemove(mapflag)
    except:
        pass
    # shouldn't need any of these intermediary outputs
    shutil.rmtree(map_output, True)
    return copied
