import os
import shutil
import time
from _Builder import Builder


class BaseStructureBuilder(Builder):
    def __init__(self, source_pos_directory, dest_pos_directory):
        super(BaseStructureBuilder, self).__init__(source_pos_directory, dest_pos_directory)

    def build(self):
        if os.path.exists(self.dest_pos_directory):
            shutil.rmtree(self.dest_pos_directory, ignore_errors=True)

        os.makedirs(os.path.join(self.dest_pos_directory, "bin"))
        os.makedirs(os.path.join(self.dest_pos_directory, "data", "server", "bundles"))
        os.makedirs(os.path.join(self.dest_pos_directory, "data", "server", "databases"))
        os.makedirs(os.path.join(self.dest_pos_directory, "data", "server", "logs"))

        bin_file_list = [u"hv.exe", u"cfgtools.dll", u"expat.dll", u"libapr-1.dll", u"libapriconv-1.dll", u"libaprutil-1.dll", u"msgbus.dll", u"systools.dll", u"tcputil.dll", u"zlib.dll"]
        self.copy_file_list(u"bin", bin_file_list)

        bundles_file_list = [u"loader.cfg", u"license.gz"]
        self.copy_file_list(os.path.join("data", "server", "bundles"), bundles_file_list)

        root_file_list = [u"start.bat", u"stop.bat"]
        self.copy_file_list(u"", root_file_list)
