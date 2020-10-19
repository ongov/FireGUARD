"""Helper functions that don't involve arcpy"""

import os
import fnmatch

import urllib2
from urlparse import urlparse

# for downloading files
import time
import dateutil
import dateutil.parser
import datetime

def ensure_dir(dir):
    """Make sure directory exists"""
    if not os.path.exists(dir):
        os.makedirs(dir)
    # return dir so we can chain this
    return dir


def try_remove(file):
    """Try to delete file but don't worry if it doesn't work"""
    try:
        os.remove(file)
    except:
        pass


def find_files(folder, file_mask='*'):
    """Find all files matching mask recursively in folder"""
    # find all files matching mask in folder recursively and return full paths
    paths = []
    for root, dirs, files in os.walk(folder):
        for file in fnmatch.filter(files, file_mask):
            real_folder = apply(os.path.join, root.split('/'))
            path = os.path.join(real_folder, file)
            paths.append(path)
    return paths

def find_dirs(folder, file_mask='*'):
    """Find all directories matching mask recursively in folder"""
    paths = []
    for root, dirs, files in os.walk(folder):
        for dir in fnmatch.filter(dirs, file_mask):
            real_folder = apply(os.path.join, root.split('/'))
            path = os.path.join(real_folder, dir)
            # HACK: if subdirectory matches then don't match parent
            if root in paths:
                paths.remove(root)
            paths.append(path)
    return paths


# taken from previous code
def fix_timezone_offset(d):
    """ Convert from UTC to local time, respecting DST if required """
    local_offset = time.timezone
    if time.daylight:
        if time.localtime().tm_isdst > 0:
            local_offset = time.altzone
    localdelta = datetime.timedelta(seconds=-local_offset)
    # convert to local time so other ftp programs would produce same result
    return (d + localdelta).replace(tzinfo=None)


def save_http(to_dir, url, save_as=None, mode='wb', ignore_existing=False):
    """ Save file at given URL into given directory using an HTTP connection """
    logging.debug("Saving {}".format(url))
    if save_as is None:
        save_as = os.path.join(to_dir, os.path.basename(url))
    if ignore_existing and os.path.exists(save_as):
        logging.debug('Ignoring existing file')
        return save_as
    ensure_dir(to_dir)
    # we want to keep modified times matching on both ends
    do_save = True
    response = urllib2.urlopen(url)
    modlocal = None
    if 'last-modified' in response.headers.keys():
        mod = response.headers['last-modified']
        modtime = dateutil.parser.parse(mod)
        modlocal = fix_timezone_offset(modtime)
        # if file exists then compare mod times
        if os.path.isfile(save_as):
            filetime = os.path.getmtime(save_as)
            filedatetime = datetime.datetime.fromtimestamp(filetime)
            do_save = modlocal != filedatetime
    # NOTE: need to check file size too? Or should it not matter because we
    #       only change the timestamp after it's fully written
    if do_save:
        logging.info("Downloading {}".format(save_as))
        try:
            with open(save_as, mode) as f:
                f.write(response.read())
        except:
            try_remove(save_as)
            raise
        if modlocal is not None:
            tt = modlocal.timetuple()
            usetime = time.mktime(tt)
            os.utime(save_as, (usetime, usetime))
    return save_as


def save_ftp(to_dir, url, user="anonymous", password=""):
    """ Save file at given URL into given directory using an FTP connection """
    urlp = urlparse(url)
    folder = os.path.dirname(urlp.path)
    site = urlp.netloc
    filename = os.path.basename(urlp.path)
    logging.debug("Saving {}".format(filename))
    import ftplib
    ftp = ftplib.FTP(site)
    ftp.login(user, password)
    ftp.cwd(folder)
    save_as = os.path.join(to_dir, filename)
    do_save = True
    ftptime = ftp.sendcmd('MDTM {}'.format(filename))
    ftpdatetime = datetime.datetime.strptime(ftptime[4:], '%Y%m%d%H%M%S')
    ftplocal = fix_timezone_offset(ftpdatetime)
    # if file exists then compare mod times
    if os.path.isfile(save_as):
        filetime = os.path.getmtime(save_as)
        filedatetime = datetime.datetime.fromtimestamp(filetime)
        do_save = ftplocal != filedatetime
    # NOTE: need to check file size too? Or should it not matter because we
    #       only change the timestamp after it's fully written
    if do_save:
        logging.debug("Downloading {}".format(filename))
        with open(save_as, 'wb') as f:
            ftp.retrbinary('RETR {}'.format(filename), f.write)
        tt = ftplocal.timetuple()
        usetime = time.mktime(tt)
        os.utime(save_as, (usetime, usetime))
    return save_as
