"""Run FireSTARR for an individual fire"""
from __future__ import print_function

import argparse
import logging
import os
import shlex
import shutil
import sys
import timeit
import traceback

from gis import rasterize_perim
from Scenario import Scenario
from Settings import Settings
from util import ensure_dir
from util import finish_process
from util import start_process
from util import write_file
from util import try_copy

## Map of three letter acronums to the folder they reside in
FOLDER_BY_TLA = {
    'APK': r'Haliburton/ALGONQUIN PARK',
    'AUR': r'Haliburton/AURORA',
    'AYL': r'Haliburton/AYLMER',
    'BAN': r'Haliburton/BANCROFT',
    'CHA': r'Chapleau/CHAPLEAU',
    'COC': r'Cochrane/COCHRANE',
    'DRY': r'Dryden',
    'FOR': r'Fort Frances',
    'GUE': r'Haliburton/GUELPH',
    'HEA': r'Cochrane/HEARST',
    'KEM': r'Haliburton/KEMPTVILLE',
    'KEN': r'Kenora',
    'KLK': r'Timmins/KIRKLAND LAKE',
    'MID': r'Haliburton/MIDHURST',
    'NIP': r'Greenstone',
    'NOR': r'North Bay',
    'PAR': r'Parry Sound',
    'PEM': r'Haliburton/PEMBROKE',
    'PET': r'Haliburton/PETERBOROUGH',
    'RED': r'Red Lake',
    'SAU': r'Chapleau/SAULT STE MARIE',
    'SLK': r'Sioux Lookout',
    'SUD': r'Sudbury',
    'THU': r'Thunder Bay',
    'TIM': r'Timmins/TIMMINS',
    'WAW': r'Wawa',
}

def runFire(scenario):
    """!
    Run fire fore given scenario
    @param scenario Scenario to run simulations for
    @return stdout as a string
    @return stderr as a string
    """
    raster = None
    if scenario.perim:
        scenario.perim, raster = rasterize_perim(scenario.run_output,
                                                 scenario.perim,
                                                 scenario.year,
                                                 scenario.fire)
    cmd = os.path.join(Settings.HOME_DIR, Settings.BINARY)
    a = ['"' + scenario.run_output + '"', scenario.day, str(scenario.lat), str(scenario.lon), scenario.start_time]
    if scenario.keep_intensity:
        a = a + ["-i"]
    args = ' '.join(a)
    if scenario.actuals_only:
        args = args + " -a"
    if scenario.no_async:
        args += " -s"
    if scenario.current_size and 1 < int(scenario.current_size) and not raster:
        args += " --size " + str(int(scenario.current_size))
    if raster:
        args = args + ' --perim "' + raster + '"'
    if scenario.ffmc:
        args += " --ffmc " + scenario.ffmc
    if scenario.dmc:
        args += " --dmc " + scenario.dmc
    if scenario.dc:
        args += " --dc " + scenario.dc
    if scenario.apcp_0800:
        args += " --apcp_0800 " + scenario.apcp_0800
    if scenario.score:
        args += " --score " + scenario.score
    # run generated command for parsing data
    run_what = [cmd] + shlex.split(args.replace('\\', '/'))
    logging.info("Running: " + ' '.join(run_what))
    t0 = timeit.default_timer()
    stdout, stderr = finish_process(start_process(run_what, scenario.simulation_flags, Settings.HOME_DIR))
    t1 = timeit.default_timer()
    logging.info("Took {}s to run simulations".format(t1 - t0))
    return stdout, stderr

def run(config_file, args):
    """!
    Run fire based on configuartion file and command line arguments
    @param config_file Configuration file to read Scenario from
    @param args argparser to pass to Scenario
    @return None
    """
    scenario = Scenario(config_file, args)
    had_output = scenario.is_current()
    ensure_dir(os.path.dirname(scenario.run_output))
    sizes = None
    # try to find a perimeter and import it
    changed = False
    def clean_flag():
        if os.path.exists(scenario.mapflag):
            os.remove(scenario.mapflag)
    def cleanup():
        if os.path.exists(scenario.run_output):
            logging.error("Removing output after run failed for " + scenario.fire)
            shutil.rmtree(scenario.run_output, True)
        clean_flag()
    if scenario.force or not (had_output or os.path.exists(scenario.runflag)):
        # HACK: do this right away so that running more than once shouldn't do the same fire in both processes
        try:
            ensure_dir(scenario.run_output)
            write_file(scenario.run_output, "running", " ")
            stdout, stderr = runFire(scenario)
            write_file(scenario.run_output, "output.txt", '\n'.join(stdout.split('\r\n')))
            os.remove(scenario.runflag)
            changed = True
        except KeyboardInterrupt:
            # this doesn't work for some reason
            cleanup()
        except Exception as e:
            logging.fatal("Error running " + scenario.fire)
            print(e)
            traceback.print_exc()
            cleanup()
            return
    # don't delete output if maps fail
    if (changed or scenario.force_maps or scenario.check_maps) and not (scenario.no_maps or os.path.exists(scenario.runflag)):
        t0 = timeit.default_timer()
        try:
            scenario.save_point_shp()
            from mxd import makeMaps
            pdf_out = makeMaps(scenario, scenario.run_output, scenario.force_maps or changed, scenario.hide)
        except Exception as e:
            logging.fatal(e)
            traceback.print_exc()
            cleanup()
            # run didn't work before so run it now
            run(config_file, args)
        try:
            if scenario.outbase == Settings.OUTPUT_DEFAULT:
                district_folder = os.path.join(Settings.FIRE_ROOT, FOLDER_BY_TLA[scenario.fire[:3]])
                to_folder = os.path.join(district_folder, scenario.fire)
                to_file = os.path.join(to_folder, 'FireSTARR', os.path.basename(pdf_out))
                if not os.path.exists(to_folder):
                    print("*********************************************")
                    print("Need to make fire folder for {}".format(scenario.fire))
                    print("*********************************************")
                    cmd = r'C:\Windows\System32\cscript.exe'
                    run_what = [cmd, os.path.join(district_folder, "CreateFireFolder.vbe"), str(int(scenario.fire[3:]))]
                    logging.debug("Running: " + ' '.join(run_what))
                    finish_process(start_process(run_what, Settings.PROCESS_FLAGS, district_folder))
                    if not os.path.exists(to_folder):
                        logging.fatal("MAKING FOLDER FAILED")
                        sys.exit(-1)
                if not os.path.exists(to_file):
                    try_copy(pdf_out, to_file)
                csv_out = os.path.splitext(pdf_out)[0] + "_assets.csv"
                csv_to = os.path.splitext(to_file)[0] + "_assets.csv"
                if not os.path.exists(csv_to):
                    try_copy(csv_out, csv_to)
        except Exception as e:
            logging.fatal("Couldn't copy to file plan")
            print(e)
            traceback.print_exc()
            clean_flag()
        t1 = timeit.default_timer()
        logging.info("Took {}s to make maps".format(t1 - t0))

def doRun():
    """!
    Run with command line arguments
    @return None
    """
    sys.path.append(Settings.HOME_DIR)
    os.chdir(Settings.HOME_DIR)
    parser = argparse.ArgumentParser()
    parser.add_argument('scenario', type=str, help='scenario file to use')
    parser.add_argument("--check-maps", action="store_true", help="check for missing maps")
    parser.add_argument("--hide", action="store_true", help="don't show known perimeters when running past fires")
    parser.add_argument("-i", action="store_true", help="keep intensity files")
    parser.add_argument("-f", action="store_true", help="force run")
    parser.add_argument("-m", action="store_true", help="force making maps")
    parser.add_argument("-n", action="store_true", help="no maps")
    parser.add_argument("-a", action="store_true", help="use actuals")
    parser.add_argument("-p", action="store_true", help="normal priority")
    parser.add_argument("-s", action="store_true", help="sequential run")
    parser.add_argument("--score", help="target score to use")
    args = parser.parse_args()
    run(args.scenario, args)

if __name__ == '__main__':
    doRun()
