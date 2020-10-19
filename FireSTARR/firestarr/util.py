"""Helper functions that don't involve arcpy"""

import os
import fnmatch

import urllib2
from urlparse import urlparse

# for downloading files
import time
import dateutil
import dateutil.parser
from dateutil.parser import parse
import datetime
import shutil
import re
import subprocess

from log import *
from processflags import *

def ensure_dir(dir):
    """!
    Make sure directory exists
    @param dir Directory to make if it doesn't already exist
    @return Directory that was requested
    """
    if not os.path.exists(dir):
        os.makedirs(dir)
    # return dir so we can chain this
    return dir

def try_remove(file):
    """!
    Try to delete file but don't worry if it doesn't work
    @param file File to remove
    @return None
    """
    try:
        os.remove(file)
    except:
        pass

def find_files(folder, file_mask='*'):
    """!
    Find all files matching mask recursively in folder
    @param folder Directory to search for matching files
    @param file_mask Mask to match files to
    @return List of files in folder and all subfolders that match file_mask
    """
    # find all files matching mask in folder recursively and return full paths
    paths = []
    for root, dirs, files in os.walk(folder):
        for file in fnmatch.filter(files, file_mask):
            real_folder = apply(os.path.join, root.split('/'))
            path = os.path.join(real_folder, file)
            paths.append(path)
    return paths

def find_dirs(folder, file_mask='*'):
    """!
    Find all directories matching mask recursively in folder
    @param folder Directory to search for matching folders
    @param file_mask Mask to match folders to
    @return List of folders in folder and all subfolders that match file_mask
    """
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

def fix_timezone_offset(d):
    """!
    Convert from UTC to local time, respecting DST if required
    @param d UTC time to convert to local time
    @return Time in local time
    """
    local_offset = time.timezone
    if time.daylight:
        if time.localtime().tm_isdst > 0:
            local_offset = time.altzone
    localdelta = datetime.timedelta(seconds=-local_offset)
    # convert to local time so other ftp programs would produce same result
    return (d + localdelta).replace(tzinfo=None)

def save_http(to_dir, url, save_as=None, mode='wb', ignore_existing=False):
    """!
    Save file at given URL into given directory using an HTTP connection
    @param to_dir Directory to save to
    @param url URL to save from
    @param save_as File name to save to
    @param mode Mode to use while saving
    @param ignore_existing Whether or not to save if file already exists
    @return Path that file was saved to
    """
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
    """!
    Save file at given URL into given directory using an FTP connection
    @param to_dir Directory to save to
    @param url URL to save from
    @param user User name for FTP login
    @param password Password for FTP login
    @return Path that file was saved to
    """
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

def find_lines(sim_output, key, start=None):
    """!
    Find lines containing given key and remove start if provided
    @param sim_output Array of simulation output, split by line
    @param key String to look for in each line of text
    @param start String to remove from start of each matching line
    @return Array of all lines that match the key, with start removed
    """
    lines = [x for x in sim_output if -1 != x.find(key)]
    if None == start:
        return lines
    return [x[x.find(start) + len(start):] for x in lines]

def find_line(sim_output, key, start=None):
    """!
    Find the first line containing given key and remove start if provided
    @param sim_output Array of simulation output, split by line
    @param key String to look for in each line of text
    @param start String to remove from start of each matching line
    @return First line that matches the key, with start removed
    """
    return find_lines(sim_output, key, start)[0]

def parse_date(filename, year):
    """!
    Try to parse date in multiple formats
    @param filename File name to parse
    @param year Year to use when parsing file name
    @return datetime parsed from file name, or None if not found
    """
    s = os.path.basename(filename)
    try:
        #look for 8 digits starting with the year
        return parse(s[s.find(str(year)):][:8])
    except:
        try:
            #look for 8 digits ending with the year
            d = s[:s.find(str(year)) + 4][-8:]
            return datetime.datetime(int(d[-4:]), int(d[:2]), int(d[2:4]))
        except:
            pass
    return None

def parse_time(filename, fire, year):
    """!
    Try to parse time in multiple formats
    @param filename File name to parse
    @param fire Fire to remove from file name
    @param year Year to use when parsing file name
    @return datetime parsed from file name, or None if not found
    """
    base = os.path.basename(filename).replace(fire, '')
    date = None
    try:
        d = base[base.find(str(year)):][:8]
        parse(d)
        date = d
    except:
        try:
            d = s[:s.find(str(year)) + 4][-8:]
            datetime.datetime(int(d[-4:]), int(d[:2]), int(d[2:4]))
            date = d
        except:
            pass
    if not date:
        # makes no sense to have a time without a date
        return None
    base = base.replace(date, '')
    m = re.search('[0-2][0-9][0-5][0-9]', base)
    try:
        return m.group(0)
    except:
        return None

def write_file(out_dir, to_file, text):
    """!
    Write given text to file and close it
    @param out_dir Directory to output to
    @param to_file File to write to
    @param text Text to write into file
    @return None
    """
    with open(os.path.join(out_dir, to_file), "w") as text_file:
        text_file.write(text)

def read_file(in_dir, from_file):
    """!
    Read entire contents of file and close it
    @param in_dir Directory to read from
    @param from_file File to read from
    @return None
    """
    with open(os.path.join(in_dir, from_file), "r") as text_file:
        return text_file.read()

def tryForceRemove(file):
    """!
    Try to remove a file multiple ways
    @param file Name of file to remove
    @return None
    """
    try:
        if os.path.exists(file):
            os.remove(file)
    except:
        try:
            f = open(file, "r+")
            f.truncate(0)
            f.close()
        except:
            pass
    if os.path.exists(file):
        os.remove(file)

def try_copy(src, to):
    """!
    Try to copy file and do nothing if copy fails
    @param src file to copy from
    @param to file to copy to
    @return None
    """
    try:
        shutil.copyfile(src, to)
    except:
        pass

def fixK(s):
    """!
    Fix precision being shown for a value
    @param s Value to format
    @return String formatted to magnitude of it
    """
    if s >= 100000000000:
        return '{:,}B'.format(int(s / 1000000000.0))
    if s >= 1000000000:
        return '{:1.1f}B'.format(s / 1000000000.0)
    if s >= 100000000:
        return '{:1.0f}M'.format(s / 1000000.0)
    if s >= 1000000:
        return '{:1.1f}M'.format(s / 1000000.0)
    if s >= 100000:
        return '{:1.0f}K'.format(s / 1000.0)
    if s >= 1000:
        return '{:1.1f}K'.format(s / 1000.0)
    if s < 1:
        return '< 1'
    if s < 10:
        return '{}'.format(int(round(s, 0)))
    return str(int(s))

def start_process(run_what, flags, cwd):
    """!
    Start running a command using subprocess
    @param run_what Process to run
    @param flags Flags to run with
    @param cwd Directory to run in
    @return Running subprocess
    """
    logging.debug(run_what)
    p = subprocess.Popen(run_what,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           cwd=cwd,
                           creationflags=flags)
    p.args = run_what
    return p

def finish_process(process, flag=None):
    """!
    Wait until subprocess is finished and return stdout and stderr
    @param process subprocess to wait for finish of
    @param flag Flag file that should be removed when done
    @return String containing stdout text
    @return String containing stderr text
    """
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        #HACK: seems to be the exit code for ctrl + c events loop tries to run it again before it exits without this
        try:
            if flag:
                tryForceRemove(flag)
        except:
            pass
        if -1073741510 == process.returncode:
            sys.exit(process.returncode)
        raise Exception('Error running {} [{}]: '.format(process.args, process.returncode) + stderr + stdout)
    return stdout, stderr

def fixtime(fire, confirm_date, maps):
    """!
    Tweak time so that fires don't have exact same time and should sort by number
    @param fire Fire to generate time tweak number from
    @param confirm_date Base date to use for utime
    @param maps List of files to change times for
    @return None
    """
    # HACK: tweak the time a bit so that different fires should have different times
    num = int(fire[-3:])
    tt = (datetime.timedelta(seconds=num) + confirm_date).timetuple()
    usetime = time.mktime(tt)
    for map in maps:
        os.utime(map, (usetime, usetime))

def readSimOutput(run_output):
    """!
    Read simulation output file in given directory
    @param run_output Directory to read simulation output from
    @return Array of simulation output, split by line
    """
    stdout = read_file(run_output, "output.txt")
    return stdout.split('\n')

def getMapOutput(run_output):
    """!
    Create directory to put map generation temporary files in
    @param run_output Base run output folder
    @return Directory to put map generation temporary files in
    """
    return ensure_dir(os.path.join(run_output, "maps"))

def getSizeAndAssumptions(i, sim_output, days, dates):
    """!
    Generate size and assumptions strings for use on maps
    @param i Index of day to get size for
    @param sim_output Array of simulation output, split by line
    @param days Array of day numbers output by simulation
    @param dates Array of dates output by simulation
    @return String to use in size text
    @return String to use in assumptions text
    """
    # HACK: empty string doesn't work?
    sizeline = 'size at end of day ' + str(days[i]) + ': '
    actuals = find_lines(sim_output, 'Actuals size at end of day')
    sizes = actuals if actuals else find_lines(sim_output, 'Fire size at end of day')
    start_size = find_lines(sim_output, 'Initializing from size ', 'size ')
    startup = find_lines(sim_output, 'Startup indices ')
    startup = startup[0] if (len(startup) > 0) else "Startup indices are not valid"
    size = [x for x in sizes if -1 != x.find(sizeline)]
    size_split = size[0][(size[0].find(sizeline) + len(sizeline)):].split(' ')
    size_min = fmt_int(size_split[0])
    size_max = fmt_int(size_split[3])
    size_median = fmt_int(size_split[9])
    size_mean = fmt_int(size_split[6])
    txtSize = "{} ha - {} ha\n(mean {} ha, median {} ha)".format(size_min, size_max, size_mean, size_median)
    start_time = find_line(sim_output, 'Initialized WxShield with date ', ' with date ')
    sim_stats = find_line(sim_output, 'streams', 'Creating ')
    txtStartup = startup[startup.find("Startup indices "):].replace(' (', ':\n     (')
    if start_size:
        txtStartup += '\nStarted from initial size {}ha'.format(float(start_size[0].split(' ')[0]))
    txtAssumptions = "Prediction for {} 23:59\nAssuming no suppression since {}\n".format(dates[i], start_time)
    if 0 == i:
        # only show startup on first day
        txtAssumptions += txtStartup + '\n'
    txtAFFES = find_lines(sim_output, 'AFFES,{}'.format(dates[i]), '13:00,')
    if txtAFFES:
        def fixColumns(txt):
            return ' '.join(map(lambda x: str.rjust(x, 4), txt.split(',')))
        header = fixColumns(find_line(sim_output, 'Scenario,Date,', 'Scenario,Date,'))
        logging.debug(header)
        values = fixColumns(txtAFFES[0])
        logging.debug(values)
        txtAssumptions += "AFFES Forecast for point is:\n" + header + "\n" + values + "\n"
    txtAssumptions += sim_stats + '\n'
    txtAssumptions += "With no spotting, and fuels initialized so that:\n"
    txtAssumptions += '\n'.join([x for x in find_lines(sim_output, 'is treated like', 'Fuel') if "like 'Non-fuel'" not in x])
    curingline = 'Fuels for day ' + str(days[i]) + ' are '
    txtAssumptions += '\nFuels are ' + find_line(sim_output, curingline, curingline)
    return txtSize, txtAssumptions

def find_day(fname):
    """!
    Find the day of the simulation based on file name
    @param fname Name of file to parse day from
    @return Day parsed from file
    """
    a = fname.find('_') + 1
    b = fname.find('_', a)
    return 365 if "final" in fname else int(fname[a:b])

def find_date(fname):
    """!
    Find date based on file name
    @param fname Name of file to parse date from
    @return Date parsed from file
    """
    b = fname.find('_', fname.find('_') + 1)
    return "Final" if "final" in fname else fname[b + 1:-4]

def findSuffix(filename):
    """!
    Find suffix from filename
    @param filename File name to find suffix from
    @return Suffix that was used on file name
    """
    suffix = os.path.basename(filename)
    suffix = os.path.splitext(suffix)[0][suffix.index('_'):]
    if '__' in suffix:
        suffix = suffix[:suffix.index('__')]
    return suffix

def fmt_int(value):
    """!
    Format an int with commas breaking it up
    @param value Integer to format
    @return Value formatted with commas breaking it up
    """
    return "{:,}".format(int(round(float((value)))))
