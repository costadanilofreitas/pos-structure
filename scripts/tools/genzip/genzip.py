# -*- coding: utf-8 -*-
# Module name: genzip.py
# Module Description: packs UI source in a single file suitable for distribution
#
# Copyright (C) 2008 MWneo Corporation
# Copyright (C) 2018 Omega Tech Enterprises Ltd.
# (All rights transferred from MWneo Corporation to Omega Tech Enterprises Ltd.)
#

import sys
import os
import os.path
import shutil
import traceback
import zipfile
import platform

print "Python Version", platform.python_version()

# Current directory
currentdir = os.path.dirname(os.path.abspath(__file__))

# Project directory
projdir = os.path.join(currentdir, "../../../mwsdk")

# Platform directory name and library extension
mach = (platform.machine() or '').lower()
plat = (platform.system() or '').lower()
dist = (platform.dist()[0].lower()) if platform.dist()[0] else ''
mach = "x86" if mach == "amd64" and plat == "windows" else mach
PLATDIR = '{0}{1}-{2}'.format(plat, '-{0}'.format(dist) if dist else '', mach)


def abspath(pathstr):
    return os.path.abspath(os.path.join(projdir, pathstr))


# Retrieve the newest (biggest) "last modified" timestamp from the given file list
# returns 0 if a file in the list does not exist
def newest(filelist):
    newest = 0
    for fname in filter(None, filelist):
        if not os.path.exists(fname):
            if os.path.islink(fname):
                continue
            return 0
        newest = max(newest, os.path.getmtime(fname))
    return newest


# Retrieve the oldest (smallest) "last modified" timestamp from the given file list
# returns 0 if a file in the list does not exist
def oldest(filelist):
    oldest = 0
    for fname in filter(None, filelist):
        if not os.path.exists(fname):
            if os.path.islink(fname):
                continue
            return 0
        ts = os.path.getmtime(fname)
        if oldest:
            oldest = min(oldest, ts)
        else:
            oldest = ts
    return oldest


# Checks if we need to update output files, based on input dates and output dates
def need_update(inputfiles, outputfiles):
    input_time = newest(inputfiles)
    output_time = oldest(outputfiles)
    if (not output_time) or output_time < input_time:
        return True
    return False


def main(dest, srcdir, arcdir):
    # Base "bin" directory
    basedir = abspath(PLATDIR) + "/bin"
    #
    # Iterate over all directories that should be zipped
    #
    if not dest.lower().endswith('.zip'):
        dest += '.zip'
    pkgname = os.path.basename(dest)
    inputfiles = []
    for root, dirnames, filenames in os.walk(srcdir):
        for filename in filenames:
            inputfiles.append(os.path.join(root, filename))
    outputfiles = [dest, os.path.join(basedir, pkgname)]
    # Check if we need to zip this component
    if not need_update(inputfiles, outputfiles):
        return 0
    print "Generating '%s'..." % dest
    prefixlen = len(srcdir + '/')
    pkg = zipfile.ZipFile(dest, mode="w", compression=zipfile.ZIP_DEFLATED)
    for f in inputfiles:
        if f.lower().endswith('.css') or f.lower().endswith('.js'):
            pkg.write(f, os.path.join(arcdir, f[prefixlen:]))
        else:
            pkg.write(f, os.path.join(f[prefixlen:]))
    pkg.close()
    # Copy the package to platform/bin dir
    shutil.copy(dest, os.path.join(basedir, pkgname))
    print "Copied {0} to output folder: {1}".format(pkgname, basedir)
    return 1


if __name__ == "__main__":
    l = len(sys.argv)
    if l < 3 or l > 4:
        print "Usage:\n    ./genzip.py [destzip] [sourcedir] <[arcdir]>\n"
        sys.exit(255)
    try:
        arcdir = sys.argv[3] if l > 3 else ''
        qty = main(sys.argv[1], sys.argv[2], arcdir)
        if qty == 0:
            print "genzip - up to date!"
        else:
            print "genzip - finished updating %d files" % qty
    except:
        traceback.print_exc()
        sys.exit(1)
    else:
        sys.exit(0)
