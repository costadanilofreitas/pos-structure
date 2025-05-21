from _Builder import Builder
import os


class PersistNormalBuilder(Builder):
    def __init__(self, source_pos_directory, dest_pos_directory):
        super(PersistNormalBuilder, self).__init__(source_pos_directory, dest_pos_directory)

    def build(self):
        bundle_dir = os.path.join("data", "server", "bundles", "persistcomp")
        os.makedirs(os.path.join(self.dest_pos_directory, bundle_dir))
        file_list = ["loader_normal.cfg"]
        self.copy_file_list(bundle_dir, file_list)

        bin_file_list = ["apr_dbd_persistcomp.dll", "apr_dbd_sqlite3.dll", "libemv.dll", "libipcqueue.dll", "libjansson.dll", "libprintio.dll", "libseppemv.dll", "npersistagent.exe",
                         "npersistcommon.dll", "npersistcommon.exp", "npersistcommon.lib", "npersistcomp.exe", "npersistcomp.zip", "replicaext.dll", "replicator.exe", "scew.dll",
                         "scew.ilk", "simplessl.dll", "sqlite3.dll", "sqlitecmdln.exe", "svs.dll", "swmfd.dll"]
        self.copy_file_list("bin", bin_file_list)
