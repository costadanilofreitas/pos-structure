import os
import shutil
import zipfile

from application.model import UpdateStep, UpdateType, CatalogUpdateData
from application.model.customexception import ErrorRetrievingPendingUpdate, \
    NoUpdateFound, ErrorCheckingPackageIntegrity
from application.util import LoggerUtil
from helper import json_serialize, remove_accents
from systools import sys_parsefilepath
from typing import Optional

logger = LoggerUtil.get_logger_name(__name__)


class UpdaterService:
    def __init__(self, api_repository, pos_repository, working_on_update, configs):
        self.api_repository = api_repository
        self.pos_repository = pos_repository
        self.working_on_update = working_on_update
        
        update_type = UpdateType.catalog
        self.local_configs = configs.updaters[update_type.name]
        data_path = sys_parsefilepath("{HVDATADIR}")
        backup_directory = sys_parsefilepath(configs.backup_directory)
        self.genesis_databases_path = os.path.join(data_path, "../../genesis/data/server/databases")
        default_work_path = os.path.join(backup_directory, update_type.name)
        self.downloads_path = os.path.join(default_work_path, "downloads")

    def download_pending_version(self):
        # type: () -> None

        latest_server_update = self._retrieve_pending_update()
        latest_server_update_id = latest_server_update["versionNumber"]
        latest_applied_update_id = self._get_last_downloaded_version_id()
        if latest_applied_update_id != latest_server_update_id:
            logger.info("New update found: {}".format(json_serialize(latest_server_update)))
            self._insert_new_update(latest_server_update)
            
            with self.working_on_update:
                logger.info("Trying to update...")
            
                self._verify_genesis_directory()
                update_data = self.get_update_data()
                self._download_package(update_data)
        else:
            logger.info("Update already downloaded: {}".format(json_serialize(latest_server_update)))
                
    @staticmethod
    def get_package_name(update_data):
        # type: () -> str
        return str(update_data.update_id) + ".zip"

    def get_update_data(self):
        # type: () -> Optional[CatalogUpdateData]
        update_data = self.pos_repository.has_pending_update_to_apply()
        if not update_data:
            raise NoUpdateFound()
    
        logger.info("New pending update data found: {}".format(json_serialize(update_data)))
        return update_data

    @staticmethod
    def test_zip_file(zip_path):
        # type: (str) -> None
        logger.info("Validating zip file...")
    
        zip_file = zipfile.ZipFile(zip_path)
        if zip_file.testzip():
            logger.error("Failed to check package integrity. [{}] is corrupted!".format(zip_path))
            raise ErrorCheckingPackageIntegrity()
    
        logger.info("Zip file successfully validated!")
                
    def _retrieve_pending_update(self):
        # type: () -> str
        try:
            return self.api_repository.retrieve_pending_update()
        except Exception as ex:
            raise ErrorRetrievingPendingUpdate(ex)
        
    def _get_last_downloaded_version_id(self):
        # type: () -> Optional[int]
        return self.pos_repository.get_last_downloaded_version_id()
    
    def _insert_new_update(self, latest_server_update):
        # type: (dict) -> None
        logger.info("Inserting new update on database...")
        update_id = latest_server_update["versionNumber"]
        update_name = remove_accents(latest_server_update["versionName"])
        return self.pos_repository.insert_new_update(update_id, update_name)

    def _verify_genesis_directory(self):
        if not os.path.exists(self.genesis_databases_path):
            os.mkdir(self.genesis_databases_path)

    def _download_package(self, update_data):
        # type: (CatalogUpdateData) -> None
        if update_data.downloaded_date:
            return
    
        logger.info("Trying to download package...")
    
        package_name = self.get_package_name(update_data)
        update_package = os.path.join(self.downloads_path, package_name)
        logger.info("Downloading package {} and saving in {}".format(package_name, update_package))
        self._store_download_package(update_package)
        self.test_zip_file(update_package)
    
        self.pos_repository.update_step(update_data.update_id, UpdateStep.download)
    
        logger.info("Package successfully stored and validated!")

    def _store_download_package(self, update_package):
        # type: (str) -> None
        package = self.api_repository.get_latest_package()
    
        logger.info("Writing package on file...")
        with open(update_package, "wb") as zip_object:
            for chunk in package.iter_content(chunk_size=128):
                zip_object.write(chunk)
        logger.info("Package successfully written on file!")

    def create_dir(self, path):
        # type: (str) -> None
    
        if os.path.exists(path):
            self.delete_dir(path)
    
        os.mkdir(path)

    @staticmethod
    def delete_dir(path):
        # type: (str) -> None
    
        shutil.rmtree(path)
        
    @staticmethod
    def copy_directory(source_path, destination_path):
        # type: (str, str) -> None
        
        shutil.copytree(source_path, destination_path)
    
    @staticmethod
    def save_directory_zip(source_path, destination_path):
        # type: (str, str) -> None
        
        shutil.make_archive(destination_path, "zip", source_path)
        
    @staticmethod
    def delete_directory(path):
        if os.path.exists(path):
            shutil.rmtree(path)
            
    @staticmethod
    def extract_zip(zip_name, path_to_extract):
        with zipfile.ZipFile(zip_name, "r") as zip_object:
            zip_object.extractall(path_to_extract)
            
    @staticmethod
    def rename_folder(original_path, renamed_path):
        os.rename(original_path, renamed_path)
