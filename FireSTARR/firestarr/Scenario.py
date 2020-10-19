"""Scenario class"""
from __future__ import print_function

import os
from ConfigParser import SafeConfigParser
from util import *
from gis import save_point_shp

from log import *
from Settings import expandPath
from Settings import Settings
from Settings import shrinkPath

class Scenario:
    """Settings for a single fire simulation"""
    ## Command line arguments that are allowed
    POSSIBLE_ARGS = ['--check-maps', '--hide', '-i', '-f', '-m', '-n', '-a', '-p', '-s']
    def __init__(self, config_file, args):
        """!
        Read from config file
        @param config_file File to read configuration from
        @param args Parsed command-line arguments
        """
        config = SafeConfigParser()
        config_file = expandPath(config_file)
        config.read(config_file)
        def opt(key):
            """Get setting for a given option if it exists"""
            return config.get('Simulation', key) if config.has_option('Simulation', key) else None
        ## Fire to run for
        self.fire = opt('fire')
        ## Date to start simulation
        self.day = opt('day')
        ## Latitude for origin
        self.lat = opt('latitude')
        ## Longitude for origin
        self.lon = opt('longitude')
        ## Directory to output final results to
        self.out_dir = expandPath(opt('output_directory'))
        ## Size of fire at start of simulation
        self.current_size = opt('current_size')
        ## Perimeter to initialize simulation with
        self.perim = opt('perimeter')
        ## Start time for simulation
        self.start_time = opt('start_time')
        ## Directory to output simulation results to
        self.run_output = os.path.join(self.out_dir, opt('run_output'))
        ## Root path to output results to
        self.outbase = expandPath(opt('outbase'))
        ## Year to run simulation for
        self.year = config.getint('Simulation', 'year')
        ## File to use as an indicator that this simulation is running
        self.runflag = os.path.join(self.run_output, "running")
        ## UNDOCUMENTED
        self.for_time = os.path.basename(self.run_output)
        ## File to use as an indicator that the maps are being made for this simulation
        self.mapflag = os.path.join(self.out_dir, self.fire + "_" + self.for_time + "_mapsinprogress")
        ## Overridden Fine Fuel Moisture Code for startup
        self.ffmc = opt('ffmc')
        ## Overridden Duff Moisture Code for startup
        self.dmc = opt('dmc')
        ## Overridden Drought Code for startup
        self.dc = opt('dc')
        ## Overridden Accumulated Precipitation at 0800 for startup
        self.apcp_0800 = opt('apcp_0800')
        ## Set target score for WeatherSHIELD historic year picking
        self.score = opt('score')
        ## Force run, even if outputs already exist
        self.force = args.f
        ## Keep all intensity outputs for simulations
        self.keep_intensity = args.i
        ## Force making maps, even if they already exist
        self.force_maps = args.m
        ## Check if maps need to be made and do so if needed
        self.check_maps = args.check_maps
        ## Whether or not to shown known perimeters when running past fires
        self.hide = args.hide
        ## Do not make maps
        self.no_maps = args.n
        ## Run for observed weather instead of forecast
        self.actuals_only = args.a
        ## Run with a lower priority
        self.low_priority = not args.p
        ## Do not run things asynchronously
        self.no_async = args.s
        ## Flags to use for simulation subprocesses
        self.simulation_flags = CREATE_NO_WINDOW
        if self.low_priority:
            self.simulation_flags = self.simulation_flags | BELOW_NORMAL_PRIORITY_CLASS
    def is_current(self):
        """!
        Whether or not simulation output is current for this
        @return Whether or not simulation output is current for this
        """
        return os.path.exists(self.run_output) and os.path.exists(os.path.join(self.run_output, "output.txt"))
    def save_point_shp(self):
        """!
        Save a shapefile containing the origin of this fire
        @return None
        """
        save_point_shp(self.lat, self.lon, self.run_output, self.fire)


def write_config(fire, day, lat, lon, start_time, out_dir, current_size, settings):
    """!
    Write configuration file with settings for a projection run
    @param fire Fire to run for
    @param day Date to start simulation
    @param lat Latitude of origin
    @param lon Longitude of origin
    @param start_time Start time for simulation
    @param out_dir Root output directory
    @param current_size Size to start fire with
    @param settings Settings to save from
    @return Path to saved configuration file
    """
    run_output = os.path.join(out_dir, fire[:3], fire, day + "_" + start_time.replace(':', ''))
    run_output = os.path.abspath(run_output)
    ensure_dir(run_output)
    filename = os.path.join(run_output, '{}.firestarr'.format(fire))
    config = SafeConfigParser()
    config.add_section('Simulation')
    def add(key, value):
        if value is not None:
            config.set('Simulation', key, str(value))
    add('fire', fire)
    add('day', day)
    add('latitude', lat)
    add('longitude', lon)
    add('output_directory', shrinkPath(out_dir))
    add('current_size', current_size)
    perim_day = day
    if settings.for_date:
        perim_day = (parse(day) - datetime.timedelta(days=1)).strftime('%Y%m%d')
        logging.info("Starting from yesterday's perimeter for {}".format(perim_day))
    perim = settings.perimeters.find_perim(fire, day)
    if settings.use_perim and perim:
        perim_date = parse_date(perim, settings.year)
        if perim_date and perim_date == parse(day):
            perim_time = parse_time(perim, fire, settings.year) if perim else start_time
            if perim_time and perim_time > start_time:
                start_time = perim_time
                if ":" not in perim_time:
                    start_time = start_time[:2] + ":" + start_time[2:]
                logging.info("Using perimeter time of {}".format(start_time))
        add('perimeter', perim)
    add('start_time', start_time)
    add('run_output', shrinkPath(run_output))
    add('outbase', shrinkPath(settings.outbase))
    add('year', settings.year)
    add('ffmc', settings.ffmc)
    add('dmc', settings.dmc)
    add('dc', settings.dc)
    add('apcp_0800', settings.apcp_0800)
    add('score', settings.score)
    with open(filename, 'w') as outfile:
        config.write(outfile)
    return filename

