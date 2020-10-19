"""Runs a fire that didn't happen with the provided fake data"""
from __future__ import print_function

import argparse
import datetime
import multiprocessing
import os
import sys
import timeit
import traceback
import shutil
import pandas as pd
from dateutil.parser import parse
from firestarr.log import *
from firestarr.gis import *
from firestarr.sql import *
from firestarr.getWxshield import *
from firestarr.PerimeterList import *
from firestarr.Settings import *
import firestarr.shared
from firestarr.shared import *
from firestarr.util import *
from firestarr.Scenario import *
from firestarr.firestarr import *

class FakePerimeter:
    """Provides dummy function to replace real class"""
    def __init__(self):
        """!
        Intiialize with nothing
        @param self The object pointer
        """
        pass
    def find_perim(self, fire, day):
        """!
        Do nothing because we don't look for perimeters
        @param self The object pointer
        @param fire Fire to find perimeter for
        @param day Day to find perimeter for
        @return None
        """
        return None

class FakeSettings:
    """Runs FireSTARR for an imaginary fire"""
    def __init__(self):
        """!
        Parses arguments for running a fake fire
        @param self The object pointer
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("fire", help="fire number to run for")
        parser.add_argument("date", help="start date to run for")
        parser.add_argument("time", help="start time to run for")
        parser.add_argument("latitude", help="latitude of start point")
        parser.add_argument("longitude", help="longitude of start point")
        parser.add_argument("folder", help="location to save output")
        parser.add_argument("--check-maps", action="store_true", help="check for missing maps")
        parser.add_argument("--ffmc", help="override FFMC")
        parser.add_argument("--dmc", help="override DMC")
        parser.add_argument("--dc", help="override DC")
        parser.add_argument("--apcp_0800", help="override 0800 accumulated precipitation")
        parser.add_argument("--size", help="override size for fire")
        parser.add_argument("-i", action="store_true", help="keep intensity files")
        parser.add_argument("-f", action="store_true", help="force run")
        parser.add_argument("-m", action="store_true", help="force making maps")
        parser.add_argument("-n", action="store_true", help="no maps")
        parser.add_argument("-a", action="store_true", help="use actuals")
        parser.add_argument("-p", action="store_true", help="normal priority")
        parser.add_argument("-s", action="store_true", help="sequential run")
        parser.add_argument("--score", help="target score to use")
        ## Parsed command line arguments
        args = parser.parse_args()
        ## Whether or not to shown known perimeters when running past fires
        args.hide = True
        ## All command line arguments
        self.args = args
        ## Name of fake fire to run
        self.fire_mask = args.fire
        ## Date to run projeciton for
        self.for_date = args.date
        ## Location to save output
        self.folder = args.folder
        ## Latitude to start fire at
        self.lat = args.latitude
        ## Longitude to start fire at
        self.lon = args.longitude
        ## Whether or not to force running projection if output already exists
        self.force = args.f
        ## Whether or not to keep intensity maps for simulation
        self.keep_intensity = args.i
        ## Whether or not to force making map products if they already exist
        self.force_maps = args.m
        ## Whether or not to check if maps need to be made and make them if so
        self.check_maps = args.check_maps
        ## Whether or not to start from a perimeter
        self.use_perim = False
        ## Whether or not to run for fires that are out
        self.out_also = False
        ## Whether or not to not create map outputs
        self.no_maps = args.n
        ## Whether or not to shown known perimeters when running past fires
        self.hide = args.hide
        ## Whether or not to run simulation using the observed weather instead of forecast
        self.actuals_only = args.a
        ## Whether or not to run simulation with lower process priority
        self.low_priority = not args.p
        ## Whether or not to run everything sequentially instead of async where possible
        self.no_async = args.s
        ## Fine Fuel Moisture Code to override startup values with
        self.ffmc = args.ffmc
        ## Duff Moisture Code to override startup values with
        self.dmc = args.dmc
        ## Drought Code to override startup values with
        self.dc = args.dc
        ## Accumulated Precipitation at 0800 to override startup values with
        self.apcp_0800 = args.apcp_0800
        ## Size to start simulated fire with
        self.override_size = args.size if args.size else 1
        ## Flags to use for starting subprocess for simulation
        self.simulation_flags = CREATE_NO_WINDOW
        ## Target score to use for WxSHIELD long range matching
        self.score = args.score
        if self.low_priority:
            self.simulation_flags = self.simulation_flags | BELOW_NORMAL_PRIORITY_CLASS
        ## Time to start simulation for
        self.for_time = args.time
        ## Year to run projection for
        self.year = parse(self.for_date).year
        ## Base folder to output to
        self.outbase = os.path.abspath(self.folder)
        if self.actuals_only:
            self.outbase = os.path.join(os.path.realpath(os.path.join(self.outbase, "..")), "actuals")
        ## Lookup class for finding perimeters
        self.perimeters = FakePerimeter()

def doRun():
    """!
    Run fake fire
    @return None
    """
    settings = FakeSettings()
    scenario = write_config(settings.fire_mask, settings.for_date, settings.lat, settings.lon, settings.for_time, settings.outbase, settings.override_size, settings)
    t0 = timeit.default_timer()
    run(scenario, settings.args)
    t1 = timeit.default_timer()
    logging.info("Took {}s to run fire".format(t1 - t0))

if __name__ == "__main__":
    doRun()
