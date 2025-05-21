# -*- coding: utf-8 -*-
# Module name: genpypkg.py
# Module Description: packs python components in a single file suitable for distribution
#
# Copyright (C) 2008 MWneo Corporation
# Copyright (C) 2018 Omega Tech Enterprises Ltd.
# (All rights transferred from MWneo Corporation to Omega Tech Enterprises Ltd.)
#

import sys
import os
import os.path
import glob
import traceback
import zipfile
import platform
import fnmatch

print("Python Version", platform.python_version())

# Current directory
currentdir = os.path.dirname(os.path.abspath(__file__))
# Project directory
projdir = os.path.join(currentdir, "")


def abspath(pathstr):
    return os.path.abspath(os.path.join(projdir, pathstr))


def newest(file_list):
    newest = 0
    for file_name in filter(None, file_list):
        if not os.path.exists(file_name):
            if os.path.islink(file_name):
                continue
            return 0
        newest = max(newest, os.path.getmtime(file_name))
    return newest


def oldest(file_list):
    oldest = 0
    for file_name in filter(None, file_list):
        if not os.path.exists(file_name):
            if os.path.islink(file_name):
                continue
            return 0
        ts = os.path.getmtime(file_name)
        if oldest:
            oldest = min(oldest, ts)
        else:
            oldest = ts
    return oldest


def need_update(input_files, output_files):
    input_time = newest(input_files)
    output_time = oldest(output_files)
    if (not output_time) or output_time < input_time:
        return True
    return False


def main(components):
    # Quantity of compiled components
    qty_compiled = 0

    # Iterate over all components that should be packaged
    for compname, srcdir, basedir, extrasdir in components:
        srcdir = abspath(srcdir)
        pkgname = compname + ".pypkg"
        pkgfile = srcdir + "/" + pkgname
        inputfiles = glob.glob(srcdir + "/*.py")
        subpackages = []

        for folder in os.listdir(srcdir):
            if folder != ".svn" and folder != ".git" and os.path.isdir(os.path.join(srcdir, folder)) and os.path.exists(os.path.join(srcdir, folder, "__init__.py")):
                subpackages.append(folder)
        for subpackage in subpackages:
            for root, dirs, files in os.walk(os.path.join(srcdir, subpackage)):
                if '.svn' in dirs:
                    dirs.remove('.svn')
                if '.git' in dirs:
                    dirs.remove('.git')
                for file in files:
                    if file.lower().endswith(".py"):
                        inputfiles.append(os.path.join(root, file))
                    if file.lower().endswith(".pyc"):
                        continue
        output_files = [pkgfile, os.path.join(basedir, pkgname)]
        # Check if we need to compile this component
        if not need_update(inputfiles, output_files):
            continue
        print("Compiling '%s' python component..." % compname)
        qty_compiled += len(output_files)
        # The PyZipFile compiles and zips python binaries for us :)
        pkg = zipfile.PyZipFile(pkgfile, mode="w", compression=zipfile.ZIP_DEFLATED)
        # Compile every python file on the given folder, and zip the ".pyc" files
        pkg.writepy(srcdir)
        # Add sub-packages (if any)
        for subpackage in subpackages:
            pkg.writepy(os.path.join(srcdir, subpackage))
        # Add extra directories
        if extrasdir is not None:
            if extrasdir == 'ALL_FOLDERS':
                extrasdirs = []
                for folder in os.listdir(srcdir):
                    if folder != ".svn" and folder != ".git" and os.path.isdir(os.path.join(srcdir, folder)) and not os.path.exists(os.path.join(srcdir, folder, "__init__.py")):
                        extrasdirs.append(folder)
            else:
                extrasdirs = extrasdir.split(';')
            for d in extrasdirs:
                for root, dirnames, filenames in os.walk(os.path.join(srcdir, d)):
                    for filename in fnmatch.filter(filenames, '*'):
                        if filename.endswith(".pyc"):
                            continue
                        full_path = os.path.join(root, filename)
                        arcname = os.path.join(root[len(srcdir) + 1:], filename)
                        pkg.write(full_path, arcname=arcname)
                        qty_compiled += 1
                    # add symbolic links to zip
                    for dir in dirnames:
                        full_path = os.path.join(root, dir)
                        arcname = os.path.join(root[len(srcdir) + 1:], dir)
                        if os.path.islink(full_path):
                            zipinfo = zipfile.ZipInfo(arcname)
                            zipinfo.create_system = 3
                            # long type of hex val of '0xA1ED0000L',
                            # say, symlink attr magic...
                            zipinfo.external_attr = 2716663808
                            pkg.writestr(zipinfo, os.readlink(full_path))
                            qty_compiled += 1

        pkg.close()
    return qty_compiled


if __name__ == "__main__":
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage:\n    ./genpypkg.py [compname] [comp src dir] [comp output dir] [extra dirs]\n")
        sys.exit(255)
    try:
        qty = main([(sys.argv[1], sys.argv[2], sys.argv[3], (sys.argv[4] if len(sys.argv) > 4 else None))])
        if qty == 0:
            print("genpypkg - up to date!")
        else:
            print("genpypkg - finished updating [%s] files: [%d]" % (sys.argv[1], qty))
    except Exception as _:
        traceback.print_exc()
        sys.exit(1)
    else:
        sys.exit(0)
