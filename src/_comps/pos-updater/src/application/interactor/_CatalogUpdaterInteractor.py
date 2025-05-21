import os
import shutil
import zipfile
from threading import Lock
import time

from application.model import CatalogUpdateData, UpdateType, UpdateStep, UpdateStatus
from application.model.configuration import Configurations
from application.model.customexception import ErrorApplyingUpdate, NoUpdateFound, NotInsideUpdateWindow, \
    ErrorRetrievingPendingUpdate, ErrorCheckingGenesisDir, ErrorInsertingNewUpdateVersion, NotExpectedException, \
    DisabledFunctionality
from application.repository.api import CatalogUpdaterAPIRepository
from application.repository.pos import CatalogUpdaterPOSRepository
from application.service import UpdaterService
from systools import sys_parsefilepath
from typing import List
from application.util import LoggerUtil

logger = LoggerUtil.get_logger_name(__name__)


class CatalogUpdaterInteractor(object):
    def __init__(self, configs, working_on_update, api_repository, pos_repository, updater_service, enabled):
        # type: (Configurations, Lock, CatalogUpdaterAPIRepository, CatalogUpdaterPOSRepository, UpdaterService, bool) -> None # noqa

        self.working_on_update = working_on_update
        self.update_type = UpdateType.catalog
        self.api_repository = api_repository
        self.pos_repository = pos_repository
        self.updater_service = updater_service
        self.enabled = enabled

        data_path = sys_parsefilepath("{HVDATADIR}")
        work_dir = sys_parsefilepath(configs.backup_directory)
        self.databases_path = os.path.join(data_path, "databases")
        self.genesis_databases_path = os.path.join(data_path, "../../genesis/data/server/databases")
        default_work_path = os.path.join(work_dir, self.update_type.name)
        self.downloads_path = os.path.join(default_work_path, "downloads")
        self.backups_path = os.path.join(default_work_path, "backups")
        self.work_path = os.path.join(default_work_path, "work_path")

        if not os.path.exists(self.backups_path):
            os.makedirs(self.backups_path)
        if not os.path.exists(self.downloads_path):
            os.makedirs(self.downloads_path)
                
    def apply_update(self):
        # type: () -> None
        
        if not self.enabled:
            raise DisabledFunctionality()
        
        try:
            update_data = self.updater_service.get_update_data()
            if not update_data:
                return
    
            with self.working_on_update:
                logger.info("Applying update")
                self._create_backup(update_data)
                self._apply_update(update_data)
                logger.info("Update [{}] fully concluded with success!".format(update_data.update_id))

                logger.info("Skipping pending updates")
                self._skip_pending_updates()
                
                logger.info("Restarting HV...")
                self.pos_repository.restart_hv()
                time.sleep(5)
        except NoUpdateFound as _:
            logger.info("No update founded to apply")
            raise
        except NotInsideUpdateWindow as _:
            logger.info("Sleeping until enter the update window")
            raise
        except ErrorRetrievingPendingUpdate as _:
            logger.exception("Error retrieving pending update")
            raise
        except ErrorCheckingGenesisDir as _:
            logger.error("Cannot find the server genesis databases directory. Please, verify and try again")
            raise
        except ErrorInsertingNewUpdateVersion as _:
            logger.exception("Error inserting new update")
            raise
        except (NotExpectedException, Exception) as _:
            logger.exception("Not expected exception on catalog update")
            raise

    def _apply_update(self, update_data):
        # type: (CatalogUpdateData) -> None
        try:
            if update_data.applied_date:
                return
    
            logger.info("Applying package...")
    
            package_name = self.updater_service.get_package_name(update_data)
            update_package = os.path.join(self.downloads_path, package_name)
    
            self._perform_update(update_package)
            self.pos_repository.update_step(update_data.update_id, UpdateStep.apply)
    
            logger.info("Package successfully applied!")
        except Exception as ex:
            logger.exception("Error applying update")
            self._restore_backup(update_data)
            raise ErrorApplyingUpdate(ex)

    def _restore_backup(self, update_data):
        # type: (CatalogUpdateData) -> None
        logger.info("Restoring backup...")

        self.pos_repository.update_status(update_data.update_id, UpdateStatus.error)
        package_name = self.updater_service.get_package_name(update_data)
        backup_package = os.path.join(self.backups_path, package_name)

        self._perform_update(backup_package)

        logger.info("Backup successfully restored!")
        
    def _skip_pending_updates(self):
        # type: () -> None
        logger.info("Skipping old pending updates...")
        return self.pos_repository.skip_pending_updates()

    def _create_work_dir(self):
        # type: () -> None
        if os.path.exists(self.work_path):
            self._delete_work_dir()
        os.mkdir(self.work_path)

    def _delete_work_dir(self):
        # type: () -> None

        shutil.rmtree(self.work_path)

    def _get_files_to_backup(self):
        # type: () -> List[str]

        return os.listdir(os.path.join(self.genesis_databases_path))

    def _copy_files_to_backup(self, files_to_backup):
        # type: (List[str]) -> None
        
        logger.info("Coping backup files to work dir...")
        for file_to_backup in files_to_backup:
            file_path = os.path.join(self.databases_path, file_to_backup)
            shutil.copy(file_path, self.work_path)
        logger.info("Backup files successfully copied!")

    def _write_backup_zip(self, backup_package, files_to_backup):
        # type: (str, List[str]) -> None

        logger.info("Zipping backup files...")
        with zipfile.ZipFile(backup_package, "w") as zip_object:
            for file_to_backup in files_to_backup:
                file_path = os.path.join(self.work_path, file_to_backup)
                zip_object.write(file_path, file_to_backup, zipfile.ZIP_DEFLATED)
        logger.info("Backup files successfully zipped!")

    def _perform_update(self, package):
        # type: (str) -> None

        self._create_work_dir()
        self._extract_package_on_work_dir(package)
        self._copy_working_files_to_genesis()
        self._delete_work_dir()

    def _extract_package_on_work_dir(self, package):
        # type: (str) -> None

        logger.info("Extracting package on work dir...")
        with zipfile.ZipFile(package, "r") as zip_object:
            zip_object.extractall(self.work_path)
        logger.info("Package successfully extracted!")

    def _copy_working_files_to_genesis(self):
        # type: () -> None

        logger.info("Coping files to genesis...")
        files_to_apply = os.listdir(self.work_path)
        for file_to_apply in files_to_apply:
            file_path = os.path.join(self.work_path, file_to_apply)
            shutil.copy(file_path, self.genesis_databases_path)
        logger.info("Files copied with success!")

    def _create_backup(self, update_data):
        # type: (CatalogUpdateData) -> None
        if update_data.backup_date:
            return
    
        logger.info("Creating backup...")
    
        package_name = self.updater_service.get_package_name(update_data)
        backup_package = os.path.join(self.backups_path, package_name)
    
        self._create_work_dir()
        files_to_backup = self._get_files_to_backup()
        self._copy_files_to_backup(files_to_backup)
        self._write_backup_zip(backup_package, files_to_backup)
        self.updater_service.test_zip_file(backup_package)
        self._delete_work_dir()
    
        self.pos_repository.update_step(update_data.update_id, UpdateStep.backup)
    
        logger.info("Backup successfully created!")
