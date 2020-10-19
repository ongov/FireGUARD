"""Settings class"""
from __future__ import print_function

import argparse
import datetime
import multiprocessing
import os
import sys

from dateutil.parser import parse

from processflags import *
from util import read_file

def getHomeDir():
    """!
    Get home directory to be used as root
    @return Home directory that everything is relative to
    """
    def get_orig():
        try:
            return os.path.dirname(os.path.realpath(__import__("__main__").__file__))
        except:
            return os.path.realpath('.')
    r = get_orig()
    if r.endswith('firestarr'):
        r = r[:-len('firestarr')]
    return r

def getRasterRoot():
    """!
    Get folder that input rasters reside in
    @return The root folder for rasters
    """
    with open(os.path.join(getHomeDir(), "settings.ini")) as f:
        content = f.readlines()
    raster_root = [x for x in content if 'RASTER_ROOT' in x][0]
    raster_root = raster_root[raster_root.find('=') + 1:].strip()
    return raster_root

def shrinkPath(path):
    """!
    Reduce path to be relative to home directory
    @param path Path to make releative to home directory
    @return Path relative to home directory, if it's a subfolder
    """
    home_dir = getHomeDir()
    if path.startswith(home_dir):
        path = path.replace(home_dir + "\\", '')
    return path

def expandPath(path):
    """!
    Expand path to include home directory
    @param path Path to expand to include home directory
    @return Path expanded to include home directory
    """
    if os.path.realpath(path) != path:
        #~ path = os.path.realpath(path)
        path = os.path.join(getHomeDir(), path)
    if os.path.abspath(path) != path:
        path = os.path.abspath(path)
    return path

def readCommon(name):
    """!
    Read a setting from the common settings folder
    @param name Name of setting file to read
    @return Contents of setting file
    """
    return read_file(os.path.realpath(os.path.join(getHomeDir(), '..\\settings')), name)

class Settings:
    """Provides settings for running FireSTARR"""
    ## Version number
    VERSION = "FireSTARR v0.9.0"
    ## Home directory that things are relative to
    HOME_DIR = getHomeDir()
    ## Root directory for raster inputs
    RASTER_DIR = expandPath(getRasterRoot())
    ## Directory with RamPART inputs
    RAMPART_DIR = os.path.join(RASTER_DIR, 'rampart')
    ## File mask to use for RamPART inputs
    RAMPART_MASK = os.path.join(RAMPART_DIR, r'weighted_{}{}.tif')
    ## Directory that GIS input data resides in
    DATA_DIR = expandPath(r'..\data')
    ## File name for export of DFOSS archive
    DFOSS_ARCHIVE = os.path.join(DATA_DIR, "AFFMARCHIVE_DFS_FIRE_ARCHIVE.csv")
    ## Default output directory
    OUTPUT_DEFAULT = readCommon('output_default')
    ## Executable to run when running simulations
    BINARY = r'Release\firestarr.exe'
    ## Flags to use for running subprocesses
    PROCESS_FLAGS = CREATE_NO_WINDOW | ABOVE_NORMAL_PRIORITY_CLASS
    ## Maximum number of threads to use
    POOL_SIZE = max(1, multiprocessing.cpu_count() / 3)
    ## Email address to put on maps
    EMAIL = readCommon('email')
    ## Active offer for accessibility that goes on all maps
    ACTIVE_OFFER = readCommon('active_offer') + EMAIL
    ## Folder to save fires to when running for current fires
    FIRE_ROOT = readCommon('fire_root')
    ## Root folder for perimeters from current year
    PERIM_ROOT = readCommon('perim_root')
    ## Root folder mask for archived perimeters for given year
    PERIM_ARCHIVE_ROOT = readCommon('perim_archive_root')
    def __init__(self):
        """Parse command line arguments and load other settings"""
        parser = argparse.ArgumentParser()
        parser.add_argument("--fire", help="fire number to run for")
        parser.add_argument("--date", help="start date to run for")
        parser.add_argument("--folder", help="location to save output")
        parser.add_argument("--resume", help="fire number to resume from")
        parser.add_argument("--check-maps", action="store_true", help="check for missing maps")
        parser.add_argument("--clean", action="store_true", help="clean failed runs")
        parser.add_argument("--year", help="specify year for fires")
        parser.add_argument("--ffmc", help="override FFMC")
        parser.add_argument("--dmc", help="override DMC")
        parser.add_argument("--dc", help="override DC")
        parser.add_argument("--apcp_0800", help="override 0800 accumulated precipitation")
        parser.add_argument("--size", help="override size for fire")
        parser.add_argument("--hide", action="store_true", help="don't show known perimeters when running past fires")
        parser.add_argument("--sequential", action="store_true", help="run one simulation at a time")
        parser.add_argument("-r", action="store_true", help="run through in reverse")
        parser.add_argument("-i", action="store_true", help="keep intensity files")
        parser.add_argument("-f", action="store_true", help="force run")
        parser.add_argument("-m", action="store_true", help="force making maps")
        parser.add_argument("-o", action="store_true", help="run for OUT fires also")
        parser.add_argument("-n", action="store_true", help="no maps")
        parser.add_argument("-c", action="store_true", help="run with current indices")
        parser.add_argument("-d", action="store_true", help="don't run make")
        parser.add_argument("-a", action="store_true", help="use actuals")
        parser.add_argument("-p", action="store_true", help="normal priority")
        parser.add_argument("-s", action="store_true", help="don't use parallel code for simulations")
        parser.add_argument("--score", help="target score to use")
        ## Parsed command line arguments
        args = parser.parse_args()
        ## All command line arguments
        self.args = args
        ## Mask to match fires to run against (e.g. 'S' would match 'SUD', 'SLK', etc.)
        self.fire_mask = args.fire
        ## Mask to define which fire we should resume running from
        self.resume_mask = args.resume
        ## Whether or not we should clean up the output directory instead of running
        self.clean = args.clean
        ## Start date to run for
        self.for_date = args.date
        ## Location to save output
        self.folder = args.folder
        ## Force run, even if outputs already exist
        self.force = args.f
        ## Keep all intensity outputs for simulations
        self.keep_intensity = args.i
        ## Force making maps, even if they already exist
        self.force_maps = args.m
        ## Check if maps need to be made and do so if needed
        self.check_maps = args.check_maps
        ## Run for fires that are currently out too
        self.out_also = args.o
        ## Do not make maps
        self.no_maps = args.n
        ## Run with current perimeter if there is one
        self.use_perim = args.c
        ## Whether or not to shown known perimeters when running past fires
        self.hide = args.hide
        ## Do not run make for C++ before beginning
        self.dont_make = args.d
        ## Run for observed weather instead of forecast
        self.actuals_only = args.a
        ## Run with a lower priority
        self.low_priority = not args.p
        ## Do not run things asynchronously
        self.no_async = args.s
        ## Run one fire at a time instead of many at once
        self.sequential = args.sequential
        ## Run through fires in reverse order
        self.reversed = args.r
        ## Overridden Fine Fuel Moisture Code for startup
        self.ffmc = args.ffmc
        ## Overridden Duff Moisture Code for startup
        self.dmc = args.dmc
        ## Overridden Drought Code for startup
        self.dc = args.dc
        ## Overridden Accumulated Precipitation at 0800 for startup
        self.apcp_0800 = args.apcp_0800
        ## Set target score for WeatherSHIELD historic year picking
        self.score = args.score
        ## Overridden size for fire to use
        self.override_size = args.size
        def showInvalid(msg):
            """!
            Message to show when arguments are invalid
            @return None
            """
            print("Called with:\n\t{}\n\n{}\n\n{}\n{}".format(' '.join(sys.argv),
                                                       msg,
                                                       parser.format_help(),
                                                       "Exiting..."))
            sys.exit(-1)
        if self.out_also and self.use_perim:
            showInvalid("Makes no sense to run using current perimeter for fires that are out")
        if args.year and self.for_date:
            self.showInvalid("Don't specify both date and year")
        if self.override_size and (not self.fire_mask or len(self.fire_mask) < 6):
            showInvalid("Can only override size for a specific fire")
        if self.clean and (self.fire_mask or self.resume_mask or self.for_date or self.force
                or self.keep_intensity or self.force_maps or self.check_maps
                or self.out_also or self.no_maps or self.use_perim or self.actuals_only):
            showInvalid("Clean prevents running other options")
        self.use_perim = self.use_perim or (not not self.for_date)
        # use less cpus because we know these will branch
        ## Flags to use for simulation subprocesses
        self.simulation_flags = CREATE_NO_WINDOW
        if self.low_priority:
            self.simulation_flags = self.simulation_flags | BELOW_NORMAL_PRIORITY_CLASS
        def current_forecast():
            t = datetime.datetime.now()
            year = t.year
            month = t.month
            day = t.day
            hour = t.hour
            # HACK: round start_time to a nice time to keep number of forecasts reasonable
            if t.hour < 10:
                # if before 10 then forecast should be for yesterday at 1500
                yesterday = t - datetime.timedelta(days=1)
                year = yesterday.year
                month = yesterday.month
                day = yesterday.day
                hour = 15
            elif t.hour < 15:
                hour = 10
            else:
                hour = 15
            return datetime.datetime(year, month, day, hour, 0, 0, 0)
        ## Time to run simulations for
        self.for_time = parse(self.for_date) if self.for_date else current_forecast()
        ## Year to run simulations for
        self.year = int(args.year) if args.year else self.for_time.year
        ## Base directory to output to
        self.outbase = Settings.OUTPUT_DEFAULT
        if self.folder:
            self.outbase = os.path.abspath(self.folder)
        elif self.year < 2020:
            self.outbase = os.path.join(self.outbase, str(self.year))
        if self.actuals_only:
            self.outbase = os.path.join(os.path.realpath(os.path.join(self.outbase, "..")), "actuals")
        ## Perimeters that have been loaded
        self.perimeters = None
    def loadPerims(self):
        """!
        Load perimeters for currently set year and fire mask
        @return None
        """
        from PerimeterList import PerimeterList
        self.perimeters = PerimeterList(self.year, self.fire_mask)
