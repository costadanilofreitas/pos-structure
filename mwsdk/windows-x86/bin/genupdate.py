#!/usr/bin/python
#
# Genesis Update application
#
# Copyright (C) 2008 MWneo Corporation
# Copyright (C) 2018 Omega Tech Enterprises Ltd.
# (All rights transferred from MWneo Corporation to Omega Tech Enterprises Ltd.)
#
# $Id$
# $Revision$
# $Date$
# Author: rrosauro. Last modified by: $Author$
#

import sys
import os
import time
import shutil
import zipfile
import tarfile
import cStringIO
from optparse import OptionParser, OptionGroup
from xml.etree import cElementTree as etree
from xml.sax import saxutils
try:
    if not os.environ.get("HVCOMPNAME"):
        os.environ["HVCOMPNAME"] = "genupdate"
    sys.path.append("./common.pypkg")
    from systools import sys_log_info, sys_log_exception
except:  # define fake log functions
    def sys_log_info(msg):
        print msg
    sys_log_debug = sys_log_warning = sys_log_error = sys_log_fatal = sys_log_exception = sys_log_info

# (Global) - command-line options
options = None
# (Global) - genupdate.py application revision number
REVISION = "$Revision$".replace("$" + "Revision: ", "").replace(" $", "")


def run_script(package, script_name, locals=None):
    """run scripts from the given update package that start with 'script_name'"""
    if (not package) or (not package.scripts):
        return
    names = [name for name in package.scripts.keys() if name.startswith(script_name)]
    names.sort()
    for script_name in names:
        script = package.scripts[script_name]
        sys_log_info("Running script: [%s]" % script_name)
        try:
            toplevel = dict(globals())
            if locals:
                toplevel.update(locals)
            exec script in toplevel
        except:
            sys_log_exception("Error executing script [%s]" % script_name)
            sys.exit(1)


def assert_folder(path):
    """ensures that the given folder exists"""
    if not os.path.exists(path):
        if options.verbose:
            sys_log_info("Creating folder [%s]" % path)
        os.makedirs(path)


def sort_packages(pkglist, folder=""):
    """sorts a list containing package names"""
    invalid_pkgs = []

    def getTS(pkgname):
        ts = 0
        try:
            pkg = GenesisPackage(os.path.join(folder, pkgname))
            ts = pkg.manifest.get("timestamp")
            pkg.close()
        except:
            invalid_pkgs.append(pkgname)
        return ts

    # try to sort and capture invalid packages
    pkglist.sort(key=getTS)

    # remove invalid packages from the list
    if len(invalid_pkgs) > 0:
        for invalid_pkg in invalid_pkgs:
            pkglist.remove(invalid_pkg)


def on_rmtree_error(func, path, exc_info):
    """called by shutil.rmtree when an error is raised"""
    os.chmod(path, 0777)
    if func == os.remove:
        try:
            func(path)
            return
        except:
            os.chmod(os.path.dirname(path), 0777)
    # Retry
    func(path)


def extract_tar(tar, path):
    """extracts all members of a tar file"""
    tar.extractall(path=path)
    # Fix symlinks manually - python bug
    if hasattr(os, 'symlink'):
        for member in tar.getmembers():
            if member.issym():
                dest = os.path.join(path, member.name)
                os.remove(dest)
                os.symlink(member.linkname, dest)


def action_backup(pkg=None):
    """implements the 'backup' action"""
    if options.verbose:
        sys_log_info("Starting genesis backup")
    bkpdir = os.path.join(options.data, "backups")
    tmptar = os.path.join(options.data, "backups", "tmp.tar")
    assert_folder(bkpdir)
    run_script(pkg, "before_backup", dict(locals()))
    # Create the tar.gz to hold genesis contents
    if options.verbose:
        sys_log_info("Compressing genesis folder...")
    tar = tarfile.open(name=tmptar, mode="w")
    tar.add(options.genesis, arcname="")
    tar.close()
    timestamp = time.strftime("%Y%m%d%H%M%S", time.gmtime())
    pkgname = "%s.genpkg" % timestamp
    pkgpath = os.path.join(bkpdir, pkgname)
    if options.verbose:
        sys_log_info("Creating file [%s]" % pkgpath)
    zip = zipfile.ZipFile(pkgpath, mode="w", compression=zipfile.ZIP_DEFLATED)
    zip.write(tmptar, arcname="genesis.tar")
    # Create the manifest
    if not pkg:
        manifest = """<?xml version='1.0' encoding='UTF-8'?>
<GenesisPackage version="1.0" type="backup" timestamp="%s" newVersion="%s">
    <Description lang="en">System backup</Description>
</GenesisPackage>
""" % (timestamp, options.currversion)
    else:
        xml = etree.XML(etree.tostring(pkg.manifest, "UTF-8"))
        xml.set("type", "backup")
        if xml.get("timestamp") is not None:
            xml.set("updateTimestamp", xml.get("timestamp"))
        xml.set("timestamp", timestamp)
        manifest = etree.tostring(xml, "UTF-8")
    zip.writestr("manifest.xml", manifest)
    # Copy package scripts if necessary
    if pkg and pkg.scripts:
        for name, data in pkg.scripts.items():
            zip.writestr("scripts/%s" % name, data)
    run_script(pkg, "after_backup", dict(locals()))
    zip.close()
    # Remove the temporary tar.gz
    os.remove(tmptar)
    if options.verbose:
        sys_log_info("Finished genesis backup")


def action_update(pkg, isrollback=False):
    """implements the 'update' and 'rollback' actions"""
    if options.verbose:
        sys_log_info("Starting genesis %s. Package: [%s]" % ("rollback" if isrollback else "update", pkg.path))
    bkpdir = os.path.join(options.data, "backups")
    assert_folder(bkpdir)
    run_script(pkg, ("before_rollback" if isrollback else "before_update"), dict(locals()))
    tar = None
    if "genesis.tar" in pkg.zip.namelist():
        genesis_old = "%s.old" % options.genesis
        if isrollback:
            # For rollback operations - delete (actually move) current genesis since backups are always full
            if os.path.exists(genesis_old):
                shutil.rmtree(genesis_old, onerror=on_rmtree_error)
            shutil.move(options.genesis, genesis_old)
        try:
            # Extract "genesis.tar" to a temporary location
            pkg.zip.extract("genesis.tar", "../updates")
            # Create a TarFile from that temporary file
            tar = tarfile.open("../updates/genesis.tar", mode="r")
            # Extract the tar.gz to the genesis folder
            extract_tar(tar, path=options.genesis)
            tar.close()
            os.remove("../updates/genesis.tar")
        except:
            if isrollback:
                # For rollback operations - restore ".old" on any exception
                try:
                    shutil.rmtree(options.genesis, onerror=on_rmtree_error)
                except:
                    pass
                os.rename(genesis_old, options.genesis)
            raise
        if isrollback:
            # For rollback operations - remove ".old" backup
            shutil.rmtree(genesis_old, onerror=on_rmtree_error)
    run_script(pkg, ("after_rollback" if isrollback else "after_update"), dict(locals()))
    if tar is not None:
        tar.close()
    if (not isrollback) and (options.move):
        # Update operations - move the applied package to "data/backups/updates"
        pkg.close()
        destdir = os.path.join(options.data, "backups/updates")
        assert_folder(destdir)
        destfile = os.path.join(destdir, os.path.basename(pkg.path))
        if options.verbose:
            sys_log_info("Moving package [%s] to [%s]" % (pkg.path, destdir))
        if os.path.exists(destfile):
            if options.verbose:
                sys_log_info("Removing existing backup: [%s]" % (destfile))
            os.remove(destfile)
        shutil.move(pkg.path, destdir)
    with open(os.path.join(options.genesis, ".genpkg_timestamp"), "w+") as fts:
        fts.write(pkg.timestamp)
    # update version string inside the .genversion
    with open(os.path.join(options.genesis, ".genversion"), "w+") as gv:
        gv.write(pkg.verstr)
    if options.verbose:
        sys_log_info("Finished genesis %s" % ("rollback" if isrollback else "update"))


def action_rollback(pkg):
    """implements the 'rollback' action"""
    action_update(pkg, isrollback=True)


def action_rollbacklast(pkg):
    """implements the 'rollbacklast' action"""
    pkgsdir = os.path.join(options.data, "backups")
    assert_folder(pkgsdir)
    names = [name for name in os.listdir(pkgsdir) if name.endswith(".genpkg")]
    if not names:
        if options.verbose:
            sys_log_info("No backups found. Ignoring --rollbacklast action")
        return
    sort_packages(names, pkgsdir)
    pkgname = names[len(names) - 1]
    pkg = GenesisPackage(os.path.join(pkgsdir, pkgname))
    action_update(pkg, isrollback=True)
    pkg.close()


def action_purge(pkg=None):
    """implements the 'purge' action"""
    if options.verbose:
        sys_log_info("Purging old genesis backups. Keep: [%d]" % options.keep)
    for basedir in ("backups", "backups/updates"):
        bkpdir = os.path.join(options.data, basedir)
        assert_folder(bkpdir)
        backups = [name for name in os.listdir(bkpdir) if name.endswith(".genpkg")]
        sort_packages(backups, bkpdir)
        to_remove = (backups[:-options.keep] if options.keep > 0 else backups)
        for file in to_remove:
            path = os.path.join(bkpdir, file)
            if options.verbose:
                sys_log_info("Purging old genesis backup: [%s]" % path)
            os.remove(path)
    if options.verbose:
        sys_log_info("Finished purging old genesis backups")


def action_listupd(pkg=None, type="updates"):
    """Implement the 'list*' actions."""
    xml = cStringIO.StringIO()
    xml.write("""<?xml version='1.0' encoding='UTF-8'?>\n""")
    xml.write("""<AvailablePackages type="%s">\n""" % type)
    pkgsdir = os.path.join(options.data, type)
    assert_folder(pkgsdir)
    pkgs = [GenesisPackage(os.path.join(pkgsdir, name)) for name in os.listdir(pkgsdir) if name.endswith(".genpkg")]

    pkgs.sort(key=lambda pkg: pkg.timestamp)
    for pkg in pkgs:
        updateTimestampAttr = "" if not pkg.manifest.get("updateTimestamp") else "updateTimestamp=%s " % saxutils.quoteattr(pkg.manifest.get("updateTimestamp")).encode("UTF-8")
        xml.write("""\t<Package timestamp=%s %spath=%s size="%d">\n""" % (saxutils.quoteattr(pkg.timestamp).encode("UTF-8"), updateTimestampAttr, saxutils.quoteattr(pkg.path), os.path.getsize(pkg.path)))
        for descr in pkg.manifest.findall("Description"):
            description = saxutils.quoteattr(descr.text) if descr.text else ""
            xml.write("""\t\t<Description lang=%s>%s</Description>\n""" % (saxutils.quoteattr(descr.get("lang")), description))

        xml.write("""\t</Package>\n""")
        pkg.close()
    xml.write("</AvailablePackages>")

    print xml.getvalue()


def action_listbkp(pkg=None, type="updates"):
    """implements the 'listbkp' action"""
    action_listupd(pkg, type="backups")


class GenesisPackage(object):

    """Represents a parsed genesis package"""
    path = None  #: Full path for the update package
    zip = None  #: zipfile.ZipFile instance
    manifest = None  #: etree.XML instance of the manifest
    timestamp = None  #: Package time-stamp
    scripts = {}    #: Dictionary of scripts
    open = True  #: Indicates if "zip" is opened
    verstr = ""    #: Version string according to the manifest

    def __init__(self, path):
        """parses a genesis package in the given path"""
        self.path = path
        self.zip = zipfile.ZipFile(path, mode="r")
        self.manifest = etree.XML(self.zip.read("manifest.xml"))
        self.timestamp = self.manifest.get("timestamp")
        self.verstr = self.manifest.get("newVersion")
        self.scripts = dict([(os.path.basename(name), self.zip.read(name)) for name in self.zip.namelist() if name.startswith("scripts/")])

    def close(self):
        """closes this package"""
        if self.open:
            self.zip.close()
        self.open = False


def main():
    global options
    # Build and parse command-line arguments
    parser = OptionParser(usage="Usage: %prog [options] <actions>", version="%prog rev. " + REVISION)
    parser.set_defaults(
        data=os.environ.get("HVDATADIR", "../data"),
        currversion=os.environ.get("MWAPP_VERSION_STRING", None),
        genesis="../genesis", verbose=True, move=True,
        packages=[], keep=5
    )
    parser.add_option("", "--package", action="append", dest="packages", metavar="FILE", help="package to apply or rollback. Each --update and --rollback actions require a corresponding --package option to be specified")
    parser.add_option("", "--data", action="store", dest="data", metavar="FOLDER", help="location of the MW:APP data folder. Default: [../data]")
    parser.add_option("", "--genesis", action="store", dest="genesis", metavar="FOLDER", help="location of the MW:APP genesis folder. Default: [../genesis]")
    parser.add_option("", "--currversion", action="store", dest="currversion", metavar="X.Y.Z", help="current MW:APP version. Default: automatically determine")
    parser.add_option("", "--keep", action="store", dest="keep", metavar="QTY", help="keep QTY newest backups when executing the --purge action. Default: [5]", type="int")
    parser.add_option("", "--quiet", action="store_false", dest="verbose", help="run quietly (no output)")
    parser.add_option("", "--nomove", action="store_false", dest="move", help="don't move applied update packages to the [data/backups/updates] folder")
    group = OptionGroup(parser, "Actions to execute", "At least one action need to be specified. Multiple actions are executed in the same order they were specified")
    group.add_option("", "--backup", action="append_const", dest="actions", const="backup", help="create a backup package of the genesis folder")
    group.add_option("", "--update", action="append_const", dest="actions", const="update", help="update the genesis folder using the update package specified by the --package option. The package will be moved to the [data/backups/updates] folder unless the option --nomove is specified")
    group.add_option("", "--rollback", action="append_const", dest="actions", const="rollback", help="restore a backup package specified by the --package option")
    group.add_option("", "--rollbacklast", action="append_const", dest="actions", const="rollbacklast", help="restore the most recent backup package")
    group.add_option("", "--purge", action="append_const", dest="actions", const="purge", help="purge old backups")
    group.add_option("", "--listupd", action="append_const", dest="actions", const="listupd", help="print an XML with the list of available updates and their descriptions. The packages are sorted from older to newer (the last listed package is the newest)")
    group.add_option("", "--listbkp", action="append_const", dest="actions", const="listbkp", help="print an XML with the list of available backups and their descriptions. The packages are sorted from older to newer (the last listed package is the newest)")
    parser.add_option_group(group)
    options, args = parser.parse_args()
    if not options.data:
        parser.error("option --data must be specified")
    if not os.path.isdir(os.path.join(options.data, "bundles")):
        parser.error("option --data must point to a valid MW:APP data folder")
    if not options.actions:
        parser.error("at least one action must be specified")
    # Check if the genesis folder is valid
    if not os.path.exists(options.genesis):
        parser.error("invalid genesis folder")
    # Check the number of packages provided
    if len(options.packages) < len(filter(lambda x: x in ("update", "rollback"), options.actions)): parser.error("exactly one '--package' must be specified for every --update and --rollback actions")
    # Execute the actions
    pkgindex = 0
    actions = {"backup": action_backup, "update": action_update, "rollback": action_rollback, "rollbacklast": action_rollbacklast, "purge": action_purge, "listupd": action_listupd, "listbkp": action_listbkp}
    for action in options.actions:
        try:
            pkg = GenesisPackage(options.packages[pkgindex]) if len(options.packages) > pkgindex else None
            actions[action](pkg)
            if action in ("update", "rollback"):
                pkgindex += 1
            if pkg:
                pkg.close()
        except:
            sys_log_exception("Unexpected exception executing action --%s" % action)
            sys.exit(1)
    # Success
    sys.exit(0)


if __name__ == "__main__":
    main()
