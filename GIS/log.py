"""Provides a way of overriding the logging method depending on whether we're in ArcMap or not"""

import logging

import sys
import os

# HACK: do this here so it outputs when run but doesn't override
## default logger
logger = logging.getLogger()
## formatter to use for log messages
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
LOG_LEVEL = "DEBUG"

class ArcpyHandler(logging.StreamHandler):
    """Overrides emit so that output is visible in ArcMap"""
    def emit(self, record):
        """Use print to output record since StreamHandler doesn't want to work in ArcMap"""
        print formatter.format(record)


def removeHandlers():
    """Remove all current logging handlers"""
    for handler in logger.handlers:
        logger.removeHandler(handler)


def addHandler():
    """Check if running in ArcMap and override handler so it just prints if we are"""
    if os.path.basename(sys.executable).lower() == 'arcmap.exe':
        handler = ArcpyHandler()
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.getLevelName(LOG_LEVEL))
    # warn about import because arcpy takes so long to load
    logging.info("Logger initialized with log level {}".format(LOG_LEVEL))


# only set up logging if we haven't already
if 0 == len(logger.handlers):
    addHandler()
