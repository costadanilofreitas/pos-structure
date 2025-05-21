# encoding: utf-8
from subprocess import Popen
import os
import time


class MwPosDriver:
    def __init__(self, mw_base_direcoty):
        self.mw_base_directory = mw_base_direcoty
        self.mw_pos_bin_directory = self.mw_base_directory + "\\bin\\"
        self.mw_pos_test_tool_directory = self.mw_base_directory + "\\data\\server\\bundles\\tests\\tools\\"
        self.stdout = None
        self.stderr = None
        self.hv_instance = None

    def build_pos_with_components(self, components_list):
        pass
    
    def start_pos(self):
        self.stdout = open(os.devnull, "w")
        self.stderr = open(os.devnull, "w")

        original = os.environ.copy()
        hv_environ = os.environ.copy()
        hv_environ.clear()


        hv_environ["HVLOGFILE"] = "..\\data\\server\\logs\\hv.log"
        # Necessário para conseguir fazer multicast
        hv_environ["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
        # Necessário para criar o sysprod.db
        hv_environ["TMP"] = os.environ["TMP"]
        # Necessário para encontrar o python
        hv_environ["PATH"] = os.environ["PATH"]

        self.hv_instance = Popen(args=[self.mw_pos_bin_directory + "hv.exe", "--service", "--data", "..\\data\\server"],
                                 stdin=None,
                                 stdout=self.stdout,
                                 stderr=self.stderr,
                                 cwd=self.mw_pos_bin_directory,
                                 env=hv_environ)

    def terminate_pos(self):
        # Send command to terminate HyperVisor
        terminate = Popen([self.mw_pos_bin_directory + "hv.exe", "--stop"], stdin=None, stderr=None, stdout=None)
        terminate.wait()
        self.hv_instance.wait()
        self.stdout.close()
        self.stderr.close()

    def restart_pos(self):
        self.terminate_pos()
        self.start_pos()

    def delete_all_databases(self):
        dbs_to_keep = ["users.db", "taxcalc.db", "product.db", "i18ncustom.db", "i18n.db", "discountcalc.db"]

        files = os.listdir(self.mw_base_directory + "\\data\\server\\databases")
        for db_file in files:
            if db_file not in dbs_to_keep:
                os.remove(os.path.join(self.mw_base_directory + "\\data\\server\\databases", db_file))

    def clean_state(self):
        clean = Popen(self.mw_pos_test_tool_directory + "clean.bat", stdin=None, stderr=None, stdout=None, cwd=self.mw_base_directory)
        clean.wait()
