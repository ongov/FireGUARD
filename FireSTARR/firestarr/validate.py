"""Run simple hit/miss validation"""
from __future__ import print_function

import fnmatch
import os
import sys
import timeit

import pandas as pd

from dateutil.parser import parse

from log import *

logging.getLogger().setLevel(logging.INFO)

from PerimeterList import PerimeterList
from gis import rasterize_perim

logging.info("Importing arcpy...")
## Start time
t0 = timeit.default_timer()
import arcpy
import arcpy.sa
from arcpy.sa import Con
from arcpy.sa import Int
from arcpy.sa import IsNull
from arcpy.sa import Raster
from arcpy.sa import SetNull
arcpy.CheckOutExtension("spatial")
## End time
t1 = timeit.default_timer()
logging.info("Took {}s to load arcpy".format(t1 - t0))

## Default folder if none specified
DEFAULT_FOLDER = r'C:\work\2019'
## Folder to run for
folder = DEFAULT_FOLDER if 1 == len(sys.argv) else sys.argv[1]

## Array of row of scores for fires
scores = []

def do_score(fire, year, day, p, shp):
    """!
    Calculate score 
    @param fire Fire to calculate score for
    @param year Year fire is from
    @param day Day score is for
    @param p Probability raster to compare to
    @param shp Shapefile for actual perimeter
    @return None
    """
    orig_raster = os.path.join(run_output, fire + ".tif")
    orig_raster = Raster(orig_raster) if os.path.exists(orig_raster) else None
    prob_raster = Raster(p)
    raster = os.path.join(run_output, os.path.splitext(os.path.basename(shp))[0] + '.tif')
    perim, raster = rasterize_perim(run_output,
                                    shp,
                                    year,
                                    fire,
                                    raster)
    if perim:
        target = Raster(raster)
        # remove the original raster used to start the simulation
        r = Con(IsNull(orig_raster), prob_raster, 0.0) if orig_raster is not None else prob_raster
        r = SetNull(r == 0.0, r)
        m = Con(IsNull(orig_raster), target, 0.0) if orig_raster is not None else target
        m = SetNull(m == 0.0, m)
        hits = Con(IsNull(r), 0.0, r) * Con(IsNull(m), 0.0, 1.0)
        misses = Con(IsNull(r), 1.0, 0.0) * Con(IsNull(m), 0.0, 1.0)
        false_positives = Con(IsNull(r), 0.0, r) * Con(IsNull(m), 1.0, 0.0)
        tp = arcpy.RasterToNumPyArray(hits, nodata_to_value=0).sum()
        fn = arcpy.RasterToNumPyArray(misses, nodata_to_value=0).sum()
        fp = arcpy.RasterToNumPyArray(false_positives, nodata_to_value=0).sum()
        total_score = tp / (tp + fn + fp)
        #~ logging.info("Scores are {} + {} + {} = {}".format(tp, fn, fp, total_score))
        scores.append([fire, year, day, p, shp, tp, fn, fp, total_score])

def do_validate(run_output):
    """!
    Validate for a specific output of probabilities
    @param run_output Folder for output to read from
    @return None
    """
    probs = map(lambda x: os.path.join(run_output, x),
                [x for x in os.listdir(run_output) if (x.startswith('wxshield_') or x.startswith('actuals_')) and x.endswith('.asc')])
    year = int(os.path.basename(run_output)[:4])
    fire = os.path.basename(os.path.dirname(run_output))
    date = os.path.basename(run_output).replace('_', ' ')
    for_date = parse(date)
    dates = map(lambda x: x[-14:-4], probs)
    for_dates = map(parse, dates)
    days = map(lambda x: (x - for_date).days + 1, for_dates)
    perim_list = PerimeterList(year, fire)
    perims = perim_list.get_perims(fire)
    if perims is not None:
        print("Validating {}".format(run_output))
        perim_rows = perims['by_date']
        perim_keys = perim_rows.keys()
        for i in xrange(len(for_dates)):
            d = for_dates[i]
            if d in perim_keys:
                p = probs[i]
                shp = perim_rows[d]
                #~ print("Comparing {} and {}".format(os.path.basename(p), os.path.basename(shp)))
                do_score(fire, year, days[i], p, shp)

def doRun():
    """!
    Run validation for all fires in root folder
    @return None
    """
    total = None
    data = []
    for root, dirs, files in os.walk(folder):
        for file in fnmatch.filter(files, "output.txt"):
            run_output = apply(os.path.join, root.split('/'))
            do_validate(run_output)
    df = pd.DataFrame(scores, columns=['Fire', 'Year', 'Day', 'Prob', 'Perim', 'Hit', 'Miss', 'False Positives', 'Total'])
    df['Prob'] = df.apply(lambda x: os.path.basename(x['Prob']), axis=1)
    df['Perim'] = df.apply(lambda x: os.path.basename(x['Perim']), axis=1)
    print(df)
    df.to_csv(os.path.join(folder, 'validate.csv'), index=False)

if __name__ == "__main__":
    doRun()
