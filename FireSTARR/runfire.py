"""Runs FireGUARD for any fires matching the criteria"""
from __future__ import print_function

import multiprocessing
import os
import shutil
import sys
import timeit
import traceback

import pandas as pd

from dateutil.parser import parse

from firestarr.log import *

from firestarr.firestarr import run
from firestarr.Scenario import Scenario
from firestarr.Scenario import write_config
from firestarr.Settings import Settings
from firestarr.sql import get_all_fires
from firestarr.sql import get_current_fires
from firestarr.sql import get_fires_by_date
from firestarr.util import ensure_dir
from firestarr.util import finish_process
from firestarr.util import start_process
from firestarr.util import try_copy
from firestarr.util import write_file

def runMake():
    """!
    Run make for project
    @return results of finished process
    """
    cmd = "make.bat"
    logging.info("Running: " + cmd)
    return finish_process(start_process(cmd, Settings.PROCESS_FLAGS, Settings.HOME_DIR))

def get_fires(settings):
    """!
    Get a list of fires based on Settings
    @param settings Settings to use for getting fires
    @return dataframe with information about fires
    """
    # HACK: disable warnings about this
    pd.options.mode.chained_assignment = None
    if 2020 == settings.year:
        use_all = not settings.for_date and (settings.out_also or settings.resume_mask or not settings.use_perim)
        # order is important because we might specify a fire and the date we want
        cols = get_all_fires(settings.fire_mask) if use_all else get_fires_by_date(settings.fire_mask, settings.for_date) if settings.for_date else get_current_fires()
        if len(cols) > 0:
            cols['day'] = cols.apply(lambda x: x['CONFIRMDATE'].strftime("%Y-%m-%d"), axis=1)
            cols['start_time'] = cols.apply(lambda x: x['CONFIRMDATE'].strftime("%H:%M"), axis=1)
            cols['FIRENAME'] = cols.apply(lambda x: x['FIRENAME'].replace(" ", ""), axis=1)
    else:
        cols = pd.read_csv(Settings.DFOSS_ARCHIVE, low_memory=False).query("FIRE_YEAR == {}".format(settings.year))
        cols.loc[:, 'FIRENAME'] = cols.apply(lambda x: '{}{:03d}'.format(x['CUR_DIST'], x['FIRE_NUMBER']), axis=1)
        if settings.fire_mask:
            cols = cols.query("FIRENAME.str.contains('{}')".format(settings.fire_mask), engine='python')
        cols = cols.query("FIRE_YEAR == {}".format(settings.year), engine='python')
        cols = cols.query("FIRE_TYPE == 'IFR'")
        def coalesce(*arg):
            return next((a for a in arg if a is not None and not pd.isnull(a)), None)
        #~ cols.loc[:, 'CONFIRMDATE'] = cols.apply(lambda x: coalesce(x['START_DATE'], x['DISC_DATE'], x['F_REP_DATE'], x['S_REP_DATE'], x['GETAWAY_DATE']), axis=1)
        # use DISC_DATE since that's what we would have had in DFOSS
        cols.loc[:, 'CONFIRMDATE'] = cols.apply(lambda x: coalesce(x['DISC_DATE'], x['F_REP_DATE'], x['S_REP_DATE'], x['GETAWAY_DATE'], x['ATTACK_DATE']), axis=1)
        #~ cols.apply(lambda x: min(x['START_DATE'], x['DISC_DATE'], x['F_REP_DATE'], x['S_REP_DATE'], x['GETAWAY_DATE']), axis=1)
        #~ cols.apply(lambda x: x['START_DATE'] if not np.isnan(x['START_DATE']) else x['DISC_DATE'] if not np.isnan(x['DISC_DATE']) else x['F_REP_DATE'] if not np.isnan(x['F_REP_DATE']) else x['S_REP_DATE'] if not np.isnan(x['S_REP_DATE']) else x['GETAWAY_DATE'], axis=1)
        cols.loc[:, 'day'] = cols.apply(lambda x: parse(x['CONFIRMDATE']).strftime("%Y-%m-%d"), axis=1)
        cols.loc[:, 'start_time'] = cols.apply(lambda x: parse(x['CONFIRMDATE']).strftime("%H:%M"), axis=1)
        cols.loc[:, 'CURRENTSIZE'] = cols['EST_DISC_SIZE']
        cols = cols[['FIRENAME', 'LATITUDE', 'LONGITUDE', 'CONFIRMDATE', 'day', 'start_time', 'CURRENTSIZE']]
    return cols

def do_clean(settings, out_dir):
    """!
    Clean up flag files in given directory that may have been left from failed runs
    @param out_dir Directory to clean
    @return None
    """
    logging.info("Running clean")
    failed = []
    for district in os.listdir(out_dir):
        d = os.path.join(out_dir, district)
        if os.path.isdir(d):
            for fire in os.listdir(d):
                f = os.path.join(d, fire)
                if os.path.isdir(f):
                    for run in os.listdir(f):
                        r = os.path.join(f, run)
                        if os.path.isdir(r):
                            runflag = os.path.join(r, "running")
                            if os.path.exists(runflag):
                                logging.info("Removing " + runflag)
                                try:
                                    os.remove(runflag)
                                except:
                                    failed.append(r)
    for district in [x for x in os.listdir(settings.outbase) if '.' not in x]:
        d = os.path.join(settings.outbase, district)
        if district <> 'output' and os.path.isdir(d):
            for file in [x for x in os.listdir(d) if '.' not in x]:
                f = os.path.join(d, file)
                if '_mapsinprogress' in f:
                    logging.info("Removing " + f)
                    try:
                        os.remove(f)
                    except:
                        failed.append(f)
                    #~ try:
                        #~ # try to remove the folder for the failed run as well
                        #~ os.remove(f.replace('_mapsinprogress'))
                    #~ except:
                        #~ pass
    if len(failed) > 0:
        logging.error("Couldn't remove some paths.  Please run the following:\n\n")
        for f in failed:
            print('del /s /q "{}"'.format(f))
    sys.exit(0)

def doRun():
    """!
    Run FireSTARR projections for all matching fires based on Settings
    @return None
    """
    settings = Settings()
    sys.path.append(Settings.HOME_DIR)
    os.chdir(Settings.HOME_DIR)
    ensure_dir(settings.outbase)
    out_dir = os.path.join(settings.outbase, "output")
    ensure_dir(out_dir)
    if settings.clean:
        do_clean(settings, out_dir)
    if not settings.dont_make:
        runMake()
    try_copy(Settings.BINARY, os.path.join(out_dir, os.path.basename(Settings.BINARY)))
    shutil.copyfile("settings.ini", os.path.join(out_dir, "settings.ini"))
    shutil.copyfile("fuel.lut", os.path.join(out_dir, "fuel.lut"))
    from mercurial import ui, hg, commands
    u = ui.ui()
    repo = hg.repository(u, ".")
    u.pushbuffer()
    commands.log(u, repo)
    output = u.popbuffer()
    write_file(out_dir, "ver.txt", output)
    u.pushbuffer()
    commands.diff(u, repo)
    output = u.popbuffer()
    write_file(out_dir, "cur.diff", output)
    #
    os.chdir(out_dir)
    #
    cols = get_fires(settings)
    #
    fires = list(cols['FIRENAME'])
    if not (settings.fire_mask or settings.resume_mask):
        logging.info("Found {:d} fires in DFOSS".format(len(fires)))
    elif settings.fire_mask:
        fires = [fire for fire in fires if str(settings.fire_mask) in fire]
    if len(fires) > 0:
        settings.loadPerims()
    # if no settings.resume_mask then we're good to start
    found_start = not settings.resume_mask
    i = 0
    to_run = []
    scenario_args = []
    for a in list(sys.argv):
        if a in Scenario.POSSIBLE_ARGS:
            scenario_args.append(a)
    for index, row in cols.sort_values(["FIRENAME"], ascending=not settings.reversed).iterrows():
        fire = row["FIRENAME"]
        found_start = found_start or settings.resume_mask in fire
        if not found_start:
            if not settings.fire_mask or fire in fires:
                i += 1
        elif fire in fires:
            logging.info("Checking fire {} {:d} of {:d}".format(fire, i + 1, len(fires)))
            print(row)
            # only run if we're not async or the fire mask is the current fire
            start_day = row["day"]
            start_time = row["start_time"]
            # make sure we're not calling this for the day it started
            if settings.use_perim and settings.for_date != start_day:
                day = settings.for_time.strftime("%Y-%m-%d")
                start_time = settings.for_time.strftime("%H:%M")
                if day == start_day:
                    if row["start_time"] > start_time:
                        start_time = row["start_time"]
            else:
                day = start_day
            lat = row["LATITUDE"]
            lon = row["LONGITUDE"]
            if not settings.fire_mask or str(settings.fire_mask) in fire:
                if not settings.for_date or settings.for_date >= start_day:
                    try:
                        #~ break
                        #~ print(fire, day, lat, lon, start_time, out_dir, int(row["CURRENTSIZE"]))
                        size = None if pd.isnull(row["CURRENTSIZE"]) else int(row["CURRENTSIZE"])
                        if settings.override_size:
                            size = int(settings.override_size)
                        scenario = write_config(fire, day, lat, lon, start_time, out_dir, size, settings)
                        if settings.fire_mask == fire or settings.sequential:
                            t0 = timeit.default_timer()
                            run(scenario, settings.args)
                            t1 = timeit.default_timer()
                            logging.debug("Took {}s to run fire".format(t1 - t0))
                        else:
                            run_what = r'python.exe firestarr\firestarr.py "{}" {}'.format(scenario, ' '.join(scenario_args))
                            to_run.append(run_what)
                    except Exception as e:
                        logging.fatal(e)
                        traceback.print_exc()
                        sys.exit(-1)
            i += 1
    if len(to_run) > 0:
        from multiprocessing.pool import ThreadPool
        tp = ThreadPool(Settings.POOL_SIZE)
        def run_process(run_what):
            # newlines were in weird places without this
            print(run_what + "\n", end='')
            finish_process(start_process(run_what, Settings.PROCESS_FLAGS, Settings.HOME_DIR))
        for run_what in to_run:
            tp.apply_async(run_process, (run_what,))
        tp.close()
        tp.join()

if __name__ == '__main__':
    doRun()