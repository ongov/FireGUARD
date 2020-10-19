"""Extract specific files from archives"""

import zipfile
import tarfile
import os
import fnmatch
import binascii
from util import find_files

# for some reason TarFile and ZipFile don't have the same attribute names
class TarFileWrapper:
    """Wraps around tarfile so that it has same attributes (that we care about) as ZipFile"""
    def infolist(self):
        """Provide function with same name as ZipFile that wraps members to have same attributes"""
        def wrapInfo(info):
            """Add new properties as aliases for existing ones to match ZipFile"""
            info.filename = info.name
            info.file_size = info.size
            return info
        return [wrapInfo(x) for x in self.tarfile.getmembers()]
    def extract(self, *args):
        """Extract data"""
        apply(self.tarfile.extract, args)
    def __enter__(self):
        """Wrapper"""
        self.tarfile.__enter__()
        return self
    def __exit__(self, type, value, traceback):
        """Wrapper"""
        self.tarfile.__exit__(type, value, traceback)
    def __init__(self, path):
        """Constructor"""
        ## Open tar file to wrap around
        self.tarfile = tarfile.open(path, "r:gz")


def check_file(output, archive, member, use_crc=False):
    """Check if file from archive should be extracted and do it if so"""
    outfile = os.path.join(output, member.filename)
    # extract if doesn't exist yet
    do_extract = not os.path.exists(outfile)
    if not do_extract:
        # file already exists, so check if file size matches
        do_extract = os.stat(outfile).st_size != member.file_size
        if do_extract:
            # shouldn't happen if exception handling works but check to be sure
            print "Replacing incomplete file"
        elif use_crc:
            crc = "N/A"
            # create a crc for the current file and compare it to the archived version
            with open(outfile, 'rb') as infile:
                buf = infile.read()
                crc = (binascii.crc32(buf) & 0xFFFFFFFF)
            do_extract = member.CRC != crc
            if do_extract:
                print "Replacing file with wrong CRC"
    if do_extract:
        print "[NEW]  " + member.filename
        try:
            archive.extract(member, output)
        except:
            try:
                # make sure file is removed if we failed to extract it
                os.remove(outfile)
            except:
                # don't worry if removal didn't work because it probably never got created
                pass
            # didn't extract, so raise the exception
            raise
    else:
        print "[OKAY] " + member.filename


def check_archive(folder, mask, wrapper, file_mask, use_crc, output=None, force=False):
    """Check folder for all matching archives and extract matching files from them"""
    if not output:
        output = os.path.join(CONFIG["DATA"], os.path.basename(os.path.normpath(folder)))
    if not force and os.path.exists(output):
        print "Output path {} already exists - not extracting".format(output)
        return
    print "Extracting to " + output
    for path in find_files(folder, file_mask):
        with wrapper(path) as archive:
            for member in archive.infolist():
                if fnmatch.fnmatch(member.filename, mask):
                    check_file(output, archive, member, use_crc)


def check_zip(folder, mask, file_mask='*.zip', use_crc=False, output=None, force=False):
    """Check folder for all matching zip archives and extract matching files from them"""
    check_archive(folder, mask, zipfile.ZipFile, file_mask, use_crc, output, force)


def check_tar(folder, mask, file_mask='*.tar.gz', use_crc=False, output=None, force=False):
    """Check folder for all matching tar archives and extract matching files from them"""
    check_archive(folder, mask, TarFileWrapper, file_mask, use_crc, output, force)

