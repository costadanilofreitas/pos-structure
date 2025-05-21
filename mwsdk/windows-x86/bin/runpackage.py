#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2008 MWneo Corporation
# Copyright (C) 2018 Omega Tech Enterprises Ltd.
# (All rights transferred from MWneo Corporation to Omega Tech Enterprises Ltd.)
#

# Runs a "main" python script, adding one or more zip packages to the path
# Usage: python runpackage.py package.pypkg [package2.pypkg] [...] [--args <program args>]
#

import argparse
import logging
import logging.config
import logging.handlers

import os
import platform
import sys
import traceback
import zipfile


class RunPackage():
    def __init__(self):
        self.config_logger()
        self.logger = logging.getLogger("RunPackage")
        self.VERSION = "1.1.0"
        self.MWPLATFORM = self.get_platform()

        # environment variables
        self.HVDATADIR = os.environ.get('HVDATADIR')
        self.BUNDLEDIR = os.environ.get('BUNDLEDIR')
        self.parse_args()
        self.add_paths()
        self.unpack()

    def get_platform(self):
        # determine platform
        system = (platform.system() or '').lower()
        distro = '-{0}'.format(platform.dist()[0].lower()) if platform.dist()[0] else ''
        ret = '{0}{1}-{2}'.format(system, distro, platform.machine())
        if ret.lower().startswith('windows'):
            ret = 'windows-x86'
        return ret

    def parse_args(self):
        description = """Helper script to run MW:APP python components"""
        parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('pkgs', nargs='+', help='packages or paths to add at runtime', metavar='PYPKG')
        parser.add_argument('--args', nargs='*', help='arguments to be passed to main()')
        parser.add_argument('--unpack-dir', help='unpack directory', default='{BUNDLEDIR}', metavar='DIR')
        parser.add_argument('--unpack', nargs='*', help='extract a directory from pypkg (e.g. mypkg.pypkg/lib)', metavar='PYPKG/dir')
        parser.add_argument('--version', action='version', version='%(prog)s v{0}'.format(self.VERSION))
        self.args = parser.parse_args()

    def add_paths(self):
        # add packages and other directories to system path
        sys.path.extend(self.args.pkgs or [])
        # extend system path to find platform-specific lib directories
        if self.HVDATADIR:
            sys.path.append(os.path.join(self.HVDATADIR, 'common', 'lib', self.MWPLATFORM))
        if self.BUNDLEDIR:
            sys.path.append(os.path.join(self.BUNDLEDIR, 'lib', self.MWPLATFORM))
            sys.path.append(os.path.join(self.BUNDLEDIR, 'python', 'lib', self.MWPLATFORM))

    def read_file(self, path):
        if os.path.exists(path):
            with open(path) as f:
                return f.read()
        return None

    def write_file(self, path, content):
        with open(path, "w+") as f:
            f.write(content)

    def unpack(self):
        # if --unpack-dir was not passed, expand the default value. If it was passed on the loader,
        # it will be already expanded by hypervisor
        if self.args.unpack_dir == '{BUNDLEDIR}':
            self.args.unpack_dir = os.path.join(self.BUNDLEDIR, '.')

        # check if unpack is necessary for this component
        if self.args.unpack:
            # make sure that output directory exists
            try:
                os.makedirs(self.args.unpack_dir)
            except:
                pass
            sl_flag = 0120000 << 16L  # symlink file type
            for path in (self.args.unpack or []):
                path_splitted = path.split('.pypkg/')
                if len(path_splitted) != 2:
                    print "Invalid unpack parameter supplied, expected format 'mypackage.pypkg/dir'"
                    continue
                pypkg, dir = ('{0}.pypkg'.format(path_splitted[0]), path_splitted[1])
                if not os.path.exists(pypkg):
                    continue
                stamp = "{0}|{1}".format(os.path.getmtime(pypkg), os.path.getsize(pypkg))
                ctlfile = os.path.join(self.args.unpack_dir, '.{0}.ctl'.format(os.path.basename(pypkg)))
                if self.read_file(ctlfile) == stamp and os.path.exists(os.path.join(self.args.unpack_dir, dir)):
                    # nothing to update
                    continue
                try:
                    archive = zipfile.ZipFile(pypkg)
                    symlinks = []
                    members = [member for member in archive.namelist() if member.startswith(dir)]
                    for member in members:
                        zipinfo = archive.getinfo(member)
                        if (zipinfo.external_attr & sl_flag) == sl_flag:
                            symlink_data = archive.read(member)
                            symlinks.append((symlink_data, os.path.join(self.args.unpack_dir, member)))
                        else:
                            archive.extract(member, path=self.args.unpack_dir)
                    # create symlinks
                    for symlink, dst in symlinks:
                        try:
                            os.symlink(symlink, dst)
                        except:
                            pass
                    self.write_file(ctlfile, stamp)
                except:
                    print "Exception extracting pypkg"

    def run(self):
        main = None
        try:
            import main
            # Check if the "main" function accepts arguments
            if main.main.func_code.co_argcount == 1:
                main.main(self.args.args or [])
            else:
                main.main()
        except:
            message = "Error starting module"
            if main:
                message = "Error on module: {}".format(main)
            self.logger.exception(message)
            traceback.print_exc(file=sys.stdout)
            raise

    @staticmethod
    def config_logger():
        filename = os.path.join('RunPackage.log')

        format_str = "%(asctime)-6s: %(name)s - %(levelname)s - %(thread)d - %(threadName)s - %(message)s"
        formatter = logging.Formatter(format_str)

        comp_logger = logging.getLogger("RunPackage")
        comp_logger.setLevel(logging.DEBUG)
        comp_logger.propagate = False

        rotating_file_logger = logging.handlers.RotatingFileHandler(filename, 'a', 5242880, 10)
        rotating_file_logger.setLevel(logging.DEBUG)
        rotating_file_logger.setFormatter(formatter)

        comp_logger.addHandler(rotating_file_logger)


if __name__ == "__main__":
    runpackage = RunPackage()
    runpackage.run()
