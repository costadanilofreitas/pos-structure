# -*- coding: utf-8 -*-

import fnmatch
import os
import re
import shutil
import sys
import urllib
import zipfile
import tarfile

from datetime import datetime
from distutils.dir_util import copy_tree, mkpath
from xml.etree import cElementTree as eTree


def logger(fn):
    global iter_count

    iter_count = 0

    def wrapper(*args, **kwargs):
        global iter_count

        start_time = datetime.now()
        try:
            time = datetime.strftime(start_time, "%H:%M:%S.%f")
            separator_string = "| " * iter_count
            print ("[{0}][START] {1}{2}".format(time, separator_string, fn.func_name))
            iter_count += 1
            return fn(*args, **kwargs)
        finally:
            end_time = datetime.now()
            diff_time = end_time - start_time
            time = datetime.strftime(end_time, "%H:%M:%S.%f")
            iter_count -= 1
            separator_string = "| " * iter_count
            exec_string = "Exec.: {}".format(diff_time)
            printed_string = "[{0}][ END ] {1}{2}".format(time, separator_string, fn.func_name)
            print ("{:<70}{}".format(printed_string, exec_string))

    return wrapper


class Util(object):
    def __init__(self, new_package=False):
        configurations = self.get_configurations()

        self.pos_folder_name = configurations["pos_folder_name"]
        self.sdk_version = configurations["sdk_version"]
        self.src_version = configurations["src_version"]

        self.current_folder = os.path.abspath(os.getcwd())
        self.current_folder = os.path.abspath(os.path.join(self.current_folder, os.pardir))
        self.current_folder = os.path.join(self.current_folder, '')

        self.install_folder = os.path.join(self.current_folder, 'install')

        self.backup_folder = os.path.join(self.current_folder, (self.pos_folder_name + "_backup"))
        self.e_deploy_pos_folder = os.path.join(self.current_folder, self.pos_folder_name)
        if new_package:
            self.e_deploy_pos_folder = self.e_deploy_pos_folder + "_downloaded"

        self.bin_folder = os.path.join(self.e_deploy_pos_folder, "bin")
        self.data_folder = os.path.join(self.e_deploy_pos_folder, "data")
        self.server_folder = os.path.join(self.data_folder, "server")
        self.ht_docs_folder = os.path.join(self.server_folder, "htdocs")
        self.python_folder = os.path.join(self.e_deploy_pos_folder, "python")
        self.src_folder = os.path.join(self.e_deploy_pos_folder, "src")
        self.scripts_folder = os.path.join(self.e_deploy_pos_folder, "scripts")

        self.is_windows = "win" in sys.platform.lower()

        self.apache_folder = os.path.join(self.e_deploy_pos_folder, "apache")
        self.apache_conf_folder = os.path.join(self.apache_folder, "conf") if self.is_windows else "/etc/httpd/conf"

        self.genesis_folder = os.path.join(self.e_deploy_pos_folder, "genesis")
        self.genesis_apache_folder = os.path.join(self.genesis_folder, "apache")
        self.genesis_bin_folder = os.path.join(self.genesis_folder, "bin")
        self.genesis_data_folder = os.path.join(self.genesis_folder, "data")
        self.genesis_python_folder = os.path.join(self.genesis_folder, "python")
        self.genesis_src_folder = os.path.join(self.genesis_folder, "src")

        self.sdk_folder = os.path.join(self.genesis_folder, "pos-core")
        self.sdk_linux_folder = os.path.join(self.sdk_folder, "linux-x86_64")
        self.sdk_windows_folder = os.path.join(self.sdk_folder, "windows-x86")

        self.sdk_repository = configurations["mwsdk_repository"]
        self.pip_install_command = configurations["pip_install_command"]
        self.apache_url = configurations["apache_url"]
        self.data_url = configurations["data_url"].format(client_store=configurations["client_store"])

    @staticmethod
    @logger
    def get_configurations():
        with open("configurations.txt") as f:
            content = f.readlines()

        configurations = {}
        for line in content:
            key = line.strip().split("=")[0]
            value = "=".join(line.strip().split("=")[1:])
            configurations[key] = value

        return configurations

    @logger
    def install(self):
        self.create_e_deploy_pos_folder()
        self.install_packages()
        self.configure_apache()
        self.create_gen_version_file()
        self.copy_bin_dependencies_to_first_run()
        self.get_executables()
        if not self.is_windows:
            self.create_genesis_sym_links()
            self.create_binary_sym_links()

        self.copy_scripts()
        self.remove_install_directory()

    @logger
    def update(self):
        self.backup()
        self.install()

    @logger
    def backup(self):
        time_now = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup_folder = os.path.join(self.backup_folder, self.pos_folder_name, ("_" + time_now))
        self.create_backup_folder(current_backup_folder)
        self.copy_to_backup_folder(current_backup_folder)

    @logger
    def create_backup_folder(self, current_backup_folder):
        if not os.path.exists(self.backup_folder):
            os.mkdir(self.backup_folder)

        os.mkdir(current_backup_folder)

    @logger
    def copy_to_backup_folder(self, current_backup_folder):
        folders = [folder for folder in os.listdir(self.e_deploy_pos_folder) if os.path.isdir(self.e_deploy_pos_folder)]
        for folder in folders:
            from_directory = os.path.join(self.e_deploy_pos_folder, folder)
            to_directory = os.path.join(current_backup_folder, folder)
            copy_tree(from_directory, to_directory)

    @logger
    def create_e_deploy_pos_folder(self):
        if os.path.exists(self.e_deploy_pos_folder):
            shutil.rmtree(self.e_deploy_pos_folder)

        os.mkdir(self.e_deploy_pos_folder)

        self.create_e_deploy_pos_child_folders()

    @logger
    def create_e_deploy_pos_child_folders(self):
        os.mkdir(self.apache_folder)
        os.mkdir(self.bin_folder)
        os.mkdir(self.data_folder)
        os.mkdir(self.genesis_folder)
        os.mkdir(self.python_folder)
        os.mkdir(self.scripts_folder)

        self.create_genesis_child_folders()

    @logger
    def create_genesis_child_folders(self):
        os.mkdir(self.genesis_apache_folder)
        os.mkdir(self.genesis_bin_folder)
        os.mkdir(self.genesis_data_folder)
        os.mkdir(self.genesis_python_folder)

    @logger
    def install_packages(self):
        self.install_sdk_package()
        self.install_src_package()
        self.install_data_package()

    @logger
    def install_sdk_package(self):
        command = self.pip_install_command.format(package_name="pos-core",
                                                  version=self.sdk_version,
                                                  install_folder=self.genesis_folder,
                                                  mwsdk_repository=self.sdk_repository)
        os.system(command)

        sdk_folders = [sdk_folder for sdk_folder in os.listdir(self.sdk_folder) if os.path.isdir(self.sdk_folder + "/" + sdk_folder)]
        self.create_genesis_sdk_folders(sdk_folders)
        self.copy_python_files()
        self.remove_sdk_folders()

    @logger
    def install_src_package(self):
        command = self.pip_install_command.format(package_name="pos-src",
                                                  version=self.src_version,
                                                  install_folder=self.genesis_folder,
                                                  mwsdk_repository=self.sdk_repository)
        os.system(command)

        package_folder = os.path.join(self.genesis_folder, "pos-src")
        server_folder = os.path.join(self.genesis_data_folder, "server")

        self.create_htdocs_folder(package_folder, server_folder)
        self.create_src_folder(package_folder)
        self.move_pypkgs_to_bin(package_folder)
        self.clean_server_packages()

    @logger
    def install_data_package(self):
        tar_file_name = os.path.join(self.genesis_data_folder, "data.tgz")
        urllib.urlretrieve(self.data_url, tar_file_name)
        tar_file = tarfile.open(tar_file_name, "r:gz")
        tar_file.extractall(self.genesis_data_folder)
        tar_file.close()
        os.remove(tar_file_name)

        self.fix_loaders_argument_paths()
        self.copy_bundles_dependencies()

    @logger
    def clean_server_packages(self):
        server_child_folders = os.listdir(self.genesis_folder)
        for folder in server_child_folders:
            if "pos-src" in folder or "pos_src" in folder:
                shutil.rmtree(os.path.join(self.genesis_folder, folder))

    @logger
    def move_pypkgs_to_bin(self, package_folder):
        pypkgs_folder = os.path.join(package_folder, "_pypkg")
        pypkgs = os.listdir(pypkgs_folder)
        binaries_folders = [os.path.join(self.genesis_bin_folder, x) for x in os.listdir(self.genesis_bin_folder)]
        for pypkg in pypkgs:
            for bin_folder in binaries_folders:
                shutil.copy(os.path.join(pypkgs_folder, pypkg), bin_folder)

    @logger
    def create_src_folder(self, package_folder):
        components_folder = os.path.join(package_folder, "_comps")
        new_components_folder = os.path.join(package_folder, "src")
        os.rename(components_folder, new_components_folder)
        shutil.move(new_components_folder, self.e_deploy_pos_folder)

    @staticmethod
    @logger
    def create_htdocs_folder(package_folder, server_folder):
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

    @logger
    def remove_sdk_folders(self):
        genesis_folders = [folder for folder in os.listdir(self.genesis_folder) if
                           os.path.isdir(os.path.join(self.genesis_folder, folder))]
        for folder in genesis_folders:
            if "pos-core" in folder or "pos_core" in folder:
                shutil.rmtree(os.path.join(self.genesis_folder, folder))

    @logger
    def create_genesis_sdk_folders(self, sdk_folders):
        for folder in sdk_folders:
            os.mkdir(os.path.join(self.genesis_apache_folder, folder))
            os.mkdir(os.path.join(self.genesis_bin_folder, folder))
            os.mkdir(os.path.join(self.genesis_python_folder, folder))

            folder_child = [sub_folder for sub_folder in os.listdir(os.path.join(self.sdk_folder, folder))
                            if os.path.isdir(os.path.join(self.sdk_folder, folder, sub_folder))]
            for sub_folder in folder_child:
                from_directory = os.path.join(self.sdk_folder, folder, sub_folder)
                to_directory = os.path.join(self.genesis_folder, sub_folder, folder)
                copy_tree(from_directory, to_directory)

    @logger
    def copy_python_files(self):
        if self.is_windows:
            copy_tree(os.path.join(self.genesis_python_folder, "windows-x86"), self.python_folder)

    @logger
    def configure_apache(self):
        if self.is_windows:
            self.download_and_install_apache()
            self.configure_apache_conf()

    @logger
    def configure_apache_conf(self):
        with open(os.path.join(self.apache_conf_folder, "httpd.conf"), 'r+') as f:
            s = f.read()
            s = self.update_srv_root(s)
            s = self.insert_apache_listen(s)
            s = self.comment_load_modules(s)
            s = self.insert_proxy_configurations(s)
            self.clean_file(f)
            f.write(s)

    @logger
    def update_srv_root(self, s):
        s = re.sub(r'^(Define SRVROOT )\".*\"', r'\1"#APACHE_FOLDER#"', s, flags=re.M)
        s = s.replace("#APACHE_FOLDER#", self.apache_folder)

        s = re.sub(r'^(DocumentRoot )\".*htdocs\"', r'\1"#HTDOCS#"', s, flags=re.M)
        s = re.sub(r'^(<Directory )\".*htdocs\"(>)', r'\1"#HTDOCS#"\2', s, flags=re.M)
        s = s.replace("#HTDOCS#", self.ht_docs_folder)

        return s

    @staticmethod
    @logger
    def insert_apache_listen(s):
        s = re.sub(r'^(Listen ).*', r'\1 8080\nProxyTimeout 60000000', s, flags=re.M)
        return s

    @staticmethod
    @logger
    def comment_load_modules(s):
        s = re.sub(r'^#(LoadModule proxy_module modules/mod_proxy.so)', r'\1', s, flags=re.M)
        s = re.sub(r'^#(LoadModule proxy_http_module modules/mod_proxy_http.so)', r'\1', s, flags=re.M)
        return s

    @staticmethod
    @logger
    def insert_proxy_configurations(s):
        s = re.sub(r'^(<Directory />)', r'ProxyTimeout 60000000\nProxyPreserveHost On\nProxyPass /mwapp http://127.0.0.1:9494/mwapp\nProxyPassReverse /mwapp http://127.0.0.1:9494/mwapp\n\n\1', s, flags=re.M)
        return s

    @staticmethod
    @logger
    def clean_file(f):
        f.seek(0)
        f.truncate()

    @logger
    def download_and_install_apache(self):
        if os.path.exists(self.apache_folder):
            shutil.rmtree(self.apache_folder)

        zip_file_name = os.path.join(self.e_deploy_pos_folder, "apache.zip")
        urllib.urlretrieve(self.apache_url, zip_file_name)

        zip_file = zipfile.ZipFile(zip_file_name)
        for f in zip_file.namelist():
            if f.startswith('Apache24'):
                zip_file.extract(f, self.e_deploy_pos_folder)
        zip_file.close()

        os.rename(os.path.join(self.e_deploy_pos_folder, "Apache24"), os.path.join(self.e_deploy_pos_folder, "apache"))
        os.remove(zip_file_name)

    @logger
    def fix_loaders_argument_paths(self):
        all_loaders = self.get_all_loaders()
        for loader in all_loaders:
            self.fix_loader_argument_paths(loader)

    @logger
    def get_all_loaders(self):
        matches = []
        for root, dir_names, file_names in os.walk(self.genesis_data_folder):
            for filename in fnmatch.filter(file_names, '*.cfg'):
                matches.append(os.path.join(root, filename))
        return matches

    @staticmethod
    def fix_loader_argument_paths(loader):
        loader_xml = eTree.parse(loader)
        for string in loader_xml.getroot().findall(".//string"):
            if string is not None and string.text is not None and "../../../src" in string.text:
                string.text = string.text.replace("../../../src", "../src")
        loader_xml.write(loader)

    @logger
    def create_genesis_sym_links(self):
        bin_folders = [self.genesis_apache_folder, self.genesis_bin_folder, self.genesis_python_folder]
        for folder in bin_folders:
            linux_path = "./linux-x86_64"
            os.symlink(linux_path, os.path.join(folder, "linux-centos-x86_64"))
            os.symlink(linux_path, os.path.join(folder, "linux-redhat-x86_64"))

    @logger
    def get_executables(self):
        if self.is_windows:
            start = "start.bat"
            stop = "stop.bat"
        else:
            start = "start.sh"
            stop = "stop.sh"

        shutil.copy(os.path.join("", "pos_files", start), self.e_deploy_pos_folder)
        shutil.copy(os.path.join("", "pos_files", stop), self.e_deploy_pos_folder)

        if not self.is_windows:
            os.chmod(os.path.join(self.e_deploy_pos_folder, start), 0775)
            os.chmod(os.path.join(self.e_deploy_pos_folder, stop), 0775)

    @logger
    def copy_bundles_dependencies(self):
        genesis_bundles = os.path.join(self.genesis_data_folder, "server", "bundles")
        loader_path = os.path.join(genesis_bundles, "loader.cfg")
        license_path = os.path.join(genesis_bundles, "license.gz")
        data_bundles = os.path.join(self.data_folder, "server", "bundles")

        mkpath(data_bundles)
        shutil.copy(loader_path, data_bundles)
        shutil.copy(license_path, data_bundles)

    @logger
    def create_gen_version_file(self):
        gen_version_file_path = os.path.join(self.genesis_folder, ".genversion")
        with open(gen_version_file_path, 'w') as f:
            f.write('1')

    @logger
    def copy_bin_dependencies_to_first_run(self):
        if self.is_windows:
            genesis_bin_folder = os.path.join(self.genesis_bin_folder, "windows-x86")
            binary_dependencies = ["genclient.exe",
                                   "libapriconv-1.dll",
                                   "systools.dll",
                                   "libaprutil-1.dll",
                                   "zlib.dll",
                                   "tcputil.dll",
                                   "expat.dll",
                                   "libapr-1.dll",
                                   "msgbus.dll",
                                   "scew.dll"]
        else:
            genesis_bin_folder = os.path.join(self.genesis_bin_folder, "linux-x86_64")
            binary_dependencies = ["genclient",
                                   "libapriconv-1.so",
                                   "libsystools.so",
                                   "libaprutil-1.so.0.3.10",
                                   "libzlib.so",
                                   "libtcputil.so",
                                   "libexpat.so",
                                   "libapr-1.so.0.4.2",
                                   "libmsgbus.so",
                                   "libscew.so"]

        for src in binary_dependencies:
            bin_path = os.path.join(genesis_bin_folder, src)
            shutil.copy(bin_path, self.bin_folder)

    @logger
    def create_binary_sym_links(self):
        binary_sys_links = {"libaprutil-1.so.0.3.10": ["libaprutil-1.so.0", "libaprutil-1.so"],
                            "libapr-1.so.0.4.2": ["libapr-1.so", "libapr-1.so.0"]}

        for binary in binary_sys_links:
            link_dest = binary_sys_links[binary]
            for dest in link_dest:
                src = "./{}".format(binary)
                dest = os.path.join(self.bin_folder, dest)
                os.symlink(src, dest)

    @logger
    def copy_scripts(self):
        copy_tree(os.path.abspath(os.getcwd()), self.scripts_folder)
        self.remove_script_files()
        self.remove_script_directories()

    @logger
    def remove_script_files(self):
        files_to_remove = ["installEdeployPOS.py", "util.pyc"]
        for file_to_remove in files_to_remove:
            file_name = os.path.join(self.scripts_folder, file_to_remove)
            self.remove_file(file_name)

    @logger
    def remove_script_directories(self):
        directories_to_remove = [".idea", "pos_files"]
        for directory_to_remove in directories_to_remove:
            directory_name = os.path.join(self.scripts_folder, directory_to_remove)
            if os.path.exists(directory_name) and os.path.isdir(directory_name):
                shutil.rmtree(directory_name)

    @logger
    def remove_install_directory(self):
        shutil.rmtree(self.install_folder)

    @staticmethod
    @logger
    def remove_file(filename):
        try:
            os.remove(filename)
        except OSError:
            pass
