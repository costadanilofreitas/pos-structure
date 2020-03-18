# -*- coding: utf-8 -*-

import fnmatch
import os
import re
import shutil
import stat
import sys
import urllib
import zipfile
from datetime import datetime
from distutils.dir_util import copy_tree
from xml.etree import cElementTree as eTree


class Util(object):
    def __init__(self, new_package=False):
        configurations = self.get_configurations()

        self.pos_folder_name = configurations["pos_folder_name"]
        self.sdk_version = configurations["sdk_version"]
        self.src_version = configurations["src_version"]

        self.current_folder = os.path.abspath(os.getcwd()).replace("\\", "/") + "/"

        self.backup_folder = self.current_folder + self.pos_folder_name + "_backup"
        self.edeploy_pos_folder = self.current_folder + self.pos_folder_name
        if new_package:
            self.edeploy_pos_folder += "_downloaded"

        self.bin_folder = self.edeploy_pos_folder + "/bin"
        self.data_folder = self.edeploy_pos_folder + "/data"
        self.htdocs_folder = self.data_folder + "/server/htdocs"
        self.python_folder = self.edeploy_pos_folder + "/python"
        self.src_folder = self.edeploy_pos_folder + "/src"

        self.apache_folder = self.edeploy_pos_folder + "/apache"
        self.apache_conf_folder = self.apache_folder + "/conf"

        self.genesis_folder = self.edeploy_pos_folder + "/genesis"
        self.genesis_apache_folder = self.genesis_folder + "/apache"
        self.genesis_bin_folder = self.genesis_folder + "/bin"
        self.genesis_data_folder = self.genesis_folder + "/data"
        self.genesis_python_folder = self.genesis_folder + "/python"
        self.genesis_src_folder = self.genesis_folder + "/src"

        self.sdk_folder = self.genesis_folder + "/mwsdk"
        self.sdk_linux_folder = self.sdk_folder + "/linux-x86_64"
        self.sdk_windows_folder = self.sdk_folder + "/windows-x86"

        self.mwsdk_repository = configurations["mwsdk_repository"]
        self.pip_install_command = configurations["pip_install_command"]
        self.apache_url = configurations["apache_url"]

        self.datas_path = "../../datas"

        self.is_windows = "win" in sys.platform.lower()

    @staticmethod
    def get_configurations():
        with open("configurations.txt") as f:
            content = f.readlines()

        configurations = {}
        for line in content:
            key = line.strip().split("=")[0]
            value = "=".join(line.strip().split("=")[1:])
            configurations[key] = value

        return configurations

    def install(self):
        print ("Starting installation")

        self.create_edeploy_pos_folder()
        self.install_packages()
        self.make_data()
        self.configure_apache()
        if not self.is_windows:
            self.create_sys_links()
        self.get_bats()

        print ("Installation finalized")

    def make_data(self):
        self.copy_datas_from_repository()
        self.fix_loaders_argument_paths()

    def update(self):
        print ("Starting update")

        self.backup()

        print ("Update finalized")

    def backup(self):
        print ("Starting backup")

        time_now = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup_folder = self.backup_folder + "/" + self.pos_folder_name + "_" + time_now
        self.create_backup_folder(current_backup_folder)
        self.copy_to_backup_folder(current_backup_folder)

        print ("Backup finalized")

    def create_backup_folder(self, current_backup_folder):
        if not os.path.exists(self.backup_folder):
            os.mkdir(self.backup_folder)

        os.mkdir(current_backup_folder)

    def copy_to_backup_folder(self, current_backup_folder):
        print ("Coping files to backup folder")

        folders = [folder for folder in os.listdir(self.edeploy_pos_folder) if os.path.isdir(self.edeploy_pos_folder)]
        for folder in folders:
            from_directory = self.edeploy_pos_folder + "/" + folder
            to_directory = current_backup_folder + "/" + folder
            copy_tree(from_directory, to_directory)

        print ("Files copied to backup folder")

    def create_edeploy_pos_folder(self):
        print ("Creating edeploy_pos folder")

        if os.path.exists(self.edeploy_pos_folder):
            print ("Removing edeploy_pos folder")
            shutil.rmtree(self.edeploy_pos_folder)

        os.mkdir(self.edeploy_pos_folder)

        self.create_edeploy_pos_child_folders()

        print ("edeploy_pos folder created")

    def create_edeploy_pos_child_folders(self):
        print ("Creating edeploy_pos child folders")

        os.mkdir(self.apache_folder)
        os.mkdir(self.bin_folder)
        os.mkdir(self.data_folder)
        os.mkdir(self.genesis_folder)
        os.mkdir(self.python_folder)
        os.mkdir(self.src_folder)

        self.create_genesis_child_folders()

        print ("edeploy_pos child folders created")

    def create_genesis_child_folders(self):
        print ("Creating genesis child folders")

        os.mkdir(self.genesis_apache_folder)
        os.mkdir(self.genesis_bin_folder)
        os.mkdir(self.genesis_data_folder)
        os.mkdir(self.genesis_python_folder)

        print ("genesis child folders created")

    def install_packages(self):
        print ("Installing packages")

        self.install_sdk_package()
        self.install_src_package()

        print ("Packages installed")

    def install_sdk_package(self):
        print ("Installing package {} in {}".format("mwsdk", self.genesis_folder))

        command = self.pip_install_command.format(package_name="mwsdk",
                                                  version=self.sdk_version,
                                                  install_folder=self.genesis_folder,
                                                  mwsdk_repository=self.mwsdk_repository)
        os.system(command)

        sdk_folders = [sdk_folder for sdk_folder in os.listdir(self.sdk_folder) if os.path.isdir(self.sdk_folder + "/" + sdk_folder)]
        self.create_genesis_sdk_folders(sdk_folders)

        self.remove_sdk_folders()

        print ("Package installed")

    def install_src_package(self):
        server_folder = os.path.join(self.genesis_data_folder, "server")

        print ("Installing package {} in {}".format("pos-src", server_folder))

        command = self.pip_install_command.format(package_name="pos-src",
                                                  version=self.src_version,
                                                  install_folder=self.genesis_folder,
                                                  mwsdk_repository=self.mwsdk_repository)
        os.system(command)

        package_folder = os.path.join(self.genesis_folder, "pos-src")

        self._create_htdocs_folder(package_folder, server_folder)
        self._create_src_folder(package_folder)
        self._move_pypkgs_to_bin(package_folder)
        self._clean_server_packages()

        print ("Package installed")

    def _clean_server_packages(self):
        server_child_folders = os.listdir(self.genesis_folder)
        for folder in server_child_folders:
            if "pos-src" in folder or "pos_src" in folder:
                shutil.rmtree(os.path.join(self.genesis_folder, folder))

    def _move_pypkgs_to_bin(self, package_folder):
        pypkgs_folder = os.path.join(package_folder, "_pypkg")
        pypkgs = os.listdir(pypkgs_folder)
        binaries_folders = [os.path.join(self.genesis_bin_folder, x) for x in os.listdir(self.genesis_bin_folder)]
        for pypkg in pypkgs:
            for bin_folder in binaries_folders:
                shutil.copy(os.path.join(pypkgs_folder, pypkg), bin_folder)

    def _create_src_folder(self, package_folder):
        components_folder = os.path.join(package_folder, "_comps")
        new_components_folder = os.path.join(package_folder, "src")
        os.rename(components_folder, new_components_folder)
        shutil.move(new_components_folder, self.genesis_folder)

    @staticmethod
    def _create_htdocs_folder(package_folder, server_folder):
        src_htdocs_folder = os.path.join(package_folder, "htdocs")
        os.rename(os.path.join(package_folder, "_guizip"), src_htdocs_folder)
        htdocs_folder = os.path.join(server_folder, "htdocs")
        shutil.move(src_htdocs_folder, htdocs_folder)
        gui_zips = os.listdir(htdocs_folder)

        for gui in gui_zips:
            gui_dir = os.path.join(htdocs_folder, gui)
            with zipfile.ZipFile(gui_dir, 'r') as zip_ref:
                zip_ref.extractall(gui_dir.split(".zip")[0])
            os.remove(gui_dir)

    def remove_sdk_folders(self):
        genesis_folders = [folder for folder in os.listdir(self.genesis_folder) if
                           os.path.isdir(self.genesis_folder + "/" + folder)]
        for folder in genesis_folders:
            if "mwsdk" in folder:
                shutil.rmtree(self.genesis_folder + "/" + folder)

    def create_genesis_sdk_folders(self, sdk_folders):
        print ("Creating genesis sdk folders")

        for folder in sdk_folders:
            print ("Creating {} folder".format(folder))

            os.mkdir(self.genesis_apache_folder + "/" + folder)
            os.mkdir(self.genesis_bin_folder + "/" + folder)
            os.mkdir(self.genesis_python_folder + "/" + folder)

            folder_child = [sub_folder for sub_folder in os.listdir(self.sdk_folder + "/" + folder) if os.path.isdir(self.sdk_folder + "/" + folder + "/" + sub_folder)]
            for sub_folder in folder_child:
                from_directory = self.sdk_folder + "/" + folder + "/" + sub_folder
                to_directory = self.genesis_folder + "/" + sub_folder + "/" + folder
                copy_tree(from_directory, to_directory)

        print ("Genesis sdk folders created")

    def configure_apache(self):
        print ("Configuring Apache")

        if self.is_windows:
            self.download_and_install_apache()
            self.configure_apache_conf()

        print ("Apache configured")

    def configure_apache_conf(self):
        with open(self.apache_conf_folder + "/httpd.conf", 'r+') as f:
            s = f.read()
            s = self.update_srv_root(s)
            s = self.insert_apache_listen(s)
            s = self.comment_load_modules(s)
            s = self.insert_proxy_configurations(s)
            self.clean_file(f)
            f.write(s)

    def update_srv_root(self, s):
        s = re.sub(r'^(Define SRVROOT )\".*\"', r'\1"#APACHE_FOLDER#"', s, flags=re.M)
        s = s.replace("#APACHE_FOLDER#", self.apache_folder)

        s = re.sub(r'^(DocumentRoot )\".*htdocs\"', r'\1"#HTDOCS#"', s, flags=re.M)
        s = re.sub(r'^(<Directory )\".*htdocs\"(>)', r'\1"#HTDOCS#"\2', s, flags=re.M)
        s = s.replace("#HTDOCS#", self.htdocs_folder)

        return s

    @staticmethod
    def insert_apache_listen(s):
        s = re.sub(r'^(Listen ).*', r'\1 8080', s, flags=re.M)
        return s

    @staticmethod
    def comment_load_modules(s):
        s = re.sub(r'^#(LoadModule proxy_module modules/mod_proxy.so)', r'\1', s, flags=re.M)
        s = re.sub(r'^#(LoadModule proxy_http_module modules/mod_proxy_http.so)', r'\1', s, flags=re.M)
        return s

    @staticmethod
    def insert_proxy_configurations(s):
        s = re.sub(r'^(<Directory />)', r'ProxyTimeout 60000000\nProxyPreserveHost On\nProxyPass /mwapp http://127.0.0.1:9494/mwapp\nProxyPassReverse /mwapp http://127.0.0.1:9494/mwapp\n\n\1', s, flags=re.M)
        return s

    @staticmethod
    def clean_file(f):
        f.seek(0)
        f.truncate()

    def download_and_install_apache(self):
        print ("Downloading and installing Apache")

        if os.path.exists(self.apache_folder):
            print ("Removing apache folder")
            shutil.rmtree(self.apache_folder)

        zip_file_name = self.edeploy_pos_folder + "/apache.zip"

        print ("Downloading Apache")
        urllib.urlretrieve(self.apache_url, zip_file_name)
        print ("Apache downloaded")

        print ("Unzip Apache")
        zip_file = zipfile.ZipFile(zip_file_name)
        for f in zip_file.namelist():
            if f.startswith('Apache24'):
                zip_file.extract(f, self.edeploy_pos_folder)
        zip_file.close()
        print ("Apache unziped")

        os.rename(self.edeploy_pos_folder + "/Apache24", self.edeploy_pos_folder + "/apache")
        os.remove(zip_file_name)

        print ("Apache downloaded and installed")

    def copy_datas_from_repository(self):
        copy_tree(self.datas_path, self.genesis_data_folder)

    def fix_loaders_argument_paths(self):
        all_loaders = self.get_all_loaders()
        for loader in all_loaders:
            self.fix_loader_argument_paths(loader)

    def get_all_loaders(self):
        matches = []
        for root, dir_names, file_names in os.walk(self.genesis_data_folder):
            for filename in fnmatch.filter(file_names, '*.cfg'):
                matches.append(os.path.join(root, filename))
        return matches

    @staticmethod
    def fix_loader_argument_paths(loader):
        loader_xml = eTree.parse(loader)
        for group in loader_xml.getroot():
            if group.get("name") != "Process":
                continue
            for key in group:
                if key.get("name") != "Arguments":
                    continue
                break
            else:
                return

            arguments = key.find("array").findall("string")
            for string in arguments:
                if "../../../" in string.text:
                    string.text = string.text.replace("../../../", "../")
            break
        loader_xml.write(loader)

    def create_sys_links(self):
        bin_folders = [self.genesis_apache_folder, self.genesis_bin_folder, self.genesis_python_folder]
        for folder in bin_folders:
            os.symlink(os.path.join(folder, "linux-x86_64"),
                       os.path.join(folder, "linux-centos-x86_64"))

    def get_bats(self):
        if self.is_windows:
            start = "start.bat"
            stop = "stop.bat"
        else:
            start = "start.sh"
            stop = "stop.sh"

        shutil.copy(os.path.join("../../", start), self.edeploy_pos_folder)
        shutil.copy(os.path.join("../../", stop), self.edeploy_pos_folder)

        if not self.is_windows:
            os.chmod(os.path.join(self.edeploy_pos_folder, start), stat.S_IXUSR | stat.S_IXGRP)
            os.chmod(os.path.join(self.edeploy_pos_folder, stop), stat.S_IXUSR | stat.S_IXGRP)

