# -*- coding: utf-8 -*-

import subprocess
from subprocess import Popen
import os


class MwPosDriver:
    def __init__(self, bin_dir, data_dir):
        self.bin_dir = bin_dir
        self.data_dir = data_dir

        self.stdout = None
        self.stderr = None
        self.hv_instance = None
    
    def start_pos(self):
        self.stdout = open(os.devnull, "w")
        self.stderr = open(os.devnull, "w")

        hv_environ = os.environ.copy()
        hv_environ.clear()

        hv_environ["HVLOGFILE"] = os.path.join(self. data_dir, "logs", "hv.log")
        # Necessário para conseguir fazer multicast
        hv_environ["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
        # Necessário para criar o sysprod.db
        hv_environ["TMP"] = os.environ["TMP"]
        # Necessário para encontrar o python
        hv_environ["PATH"] = os.environ["PATH"]

        self.hv_instance = Popen(args=[os.path.join(self.bin_dir, "hv.exe"), "--service", "--data", self.data_dir],
                                 stdin=None,
                                 stdout=self.stdout,
                                 stderr=self.stderr,
                                 cwd=self.bin_dir,
                                 env=hv_environ)

    def terminate_pos(self):
        # Send command to terminate HyperVisor
        terminate = Popen([os.path.join(self.bin_dir, "hv.exe"), "--stop"], stdin=None, stderr=None, stdout=None)
        terminate.wait()
        self.hv_instance.wait()
        self.stdout.close()
        self.stderr.close()

    def restart_pos(self):
        self.terminate_pos()
        self.start_pos()

    def is_running(self):
        list = Popen([os.path.join(self.bin_dir, "hv.exe"), "--list"],
                     stdin=None,
                     stderr=subprocess.PIPE,
                     stdout=subprocess.PIPE)
        out, err = list.communicate()
        list.wait()

        return "<compList" in out

    def delete_all_databases(self):
        dbs_to_keep = ["users.db", "taxcalc.db", "product.db", "i18ncustom.db", "i18n.db", "discountcalc.db"]

        files = os.listdir(os.path.join(self.data_dir, "databases"))
        for db_file in files:
            if db_file not in dbs_to_keep:
                os.remove(os.path.join(self.data_dir, "databases", db_file))
