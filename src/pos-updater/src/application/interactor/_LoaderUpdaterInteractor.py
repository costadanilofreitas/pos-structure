import json
import os
import time
from datetime import datetime
from threading import Lock

from application.model import UpdateType
from application.model.Payment import Payment
from application.model.configuration import Configurations
from application.model.customexception import NotExpectedException, DisabledFunctionality, ErrorCreatingBackup, \
    ErrorDeletingContent, ErrorRecoveringDatabases, ErrorExtractingLoaders, ErrorUpdatingDatabases, \
    ErrorDownloadingLoaders, RollbackError, NotInsideUpdateWindow
from application.repository.api import CatalogUpdaterAPIRepository
from application.repository.pos import LoaderUpdaterPOSRepository
from application.service import UpdaterService
from application.util import LoggerUtil, ValidationUtil
from systools import sys_parsefilepath

GENESIS_PATH = "../../genesis"

logger = LoggerUtil.get_logger_name(__name__)


class LoaderUpdaterInteractor(object):
    def __init__(self, configs, working_on_update, api_repository, pos_repository, updater_service):
        # type: (Configurations, Lock, CatalogUpdaterAPIRepository, LoaderUpdaterPOSRepository, UpdaterService) -> None # noqa

        update_type = UpdateType.loader
        update_name = update_type.name
        
        self.update_type = UpdateType.loader
        self.enabled = configs.updaters[update_name].enabled
        self.local_configs = configs.updaters[self.update_type.name]
        self.store_id = configs.store_id
        
        self.working_on_update = working_on_update
        self.api_repository = api_repository
        self.pos_repository = pos_repository
        self.updater_service = updater_service
        
        data_path = sys_parsefilepath("{HVDATADIR}")
        work_dir = sys_parsefilepath(configs.backup_directory)
        self.data_relative_path = "data"
        self.databases_relative_path = "data/server/databases"
        self.data_path = os.path.join(data_path, GENESIS_PATH, self.data_relative_path)
        self.renamed_data_path = os.path.join(data_path, GENESIS_PATH, "_" + self.data_relative_path)
        self.server_path = os.path.join(self.data_path, "server")
        self.databases_path = os.path.join(data_path, GENESIS_PATH, self.databases_relative_path)
        default_work_path = os.path.join(work_dir, self.update_type.name)
        self.downloads_path = os.path.join(default_work_path, "downloads")
        self.backups_path = os.path.join(default_work_path, "backups")
        self.work_path = os.path.join(default_work_path, "work_path")
        self.payments_json = os.path.join(self.server_path, "bundles/payments.json")
        self.loaders_zip = "loaders.zip"
        
        if not os.path.exists(self.backups_path):
            os.makedirs(self.backups_path)
        if not os.path.exists(self.downloads_path):
            os.makedirs(self.downloads_path)

    def update_loaders(self, ignore_update_window, restart_hv=False):
        # type: () -> None
        
        if not self.enabled:
            raise DisabledFunctionality()

        rollback_necessary = False
        
        try:
            with self.working_on_update:
                logger.info("Updating loaders")

                if not self.pos_repository.some_update_already_applied():
                    restart_hv = True
                elif not ignore_update_window:
                    self._check_update_window()

                self.updater_service.create_dir(self.work_path)
                self._download_new_loaders()
                self._create_backup()
                
                rollback_necessary = True
                self._rename_path(self.data_path, self.renamed_data_path)
                self._get_new_loaders()
                self._recover_databases()
                self._update_payments()
                self._delete_content(self.renamed_data_path)

                last_loader_update_id = self.pos_repository.get_last_loader_update_id()
                self.pos_repository.insert_new_loader_update(last_loader_update_id + 1, "Loaders")

                rollback_necessary = False
                if restart_hv:
                    logger.info("Restarting HV...")
                    self.pos_repository.restart_hv()
                    time.sleep(5)
                
                logger.info("Loaders update fully concluded with success!")
        except NotInsideUpdateWindow as _:
            logger.info("Sleeping until enter the update window")
            raise
        except (NotExpectedException, Exception) as _:
            if rollback_necessary:
                with self.working_on_update:
                    self._rollback()

            logger.exception("Not expected exception on loaders update")
            raise
        finally:
            self.updater_service.delete_dir(self.work_path)
            
    def _check_update_window(self):
        # type: () -> None
        start_time = self.local_configs.window.start_time
        end_time = self.local_configs.window.end_time
        if not ValidationUtil().is_inside_allowed_window(start_time, end_time):
            str_start_time = start_time.strftime("%H:%M:%S")
            str_end_time = end_time.strftime("%H:%M:%S")
            message = "Not inside allowed window. Start: {} / End: {}".format(str_start_time, str_end_time)
            logger.info(message)
            raise NotInsideUpdateWindow()
        
    def _download_new_loaders(self):
        # type: () -> None
        
        try:
            logger.info("Downloading new loaders")
            file_path = os.path.join(self.downloads_path, self.loaders_zip)
            self.api_repository.download_loaders(file_path)
            logger.info("Loaders successfully downloaded")
        except Exception as _:
            logger.exception("Error downloading loaders")
            raise ErrorDownloadingLoaders()
        
    def _create_backup(self):
        # type: () -> None

        try:
            logger.info("Creating loaders backup")

            backup_zip_name = "loaders_{}".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
            backup_package = os.path.join(self.backups_path, backup_zip_name)
            backup_package_zip = os.path.join(self.backups_path, backup_zip_name) + ".zip"

            zip_path = os.path.join(self.work_path, self.data_relative_path)
            self.updater_service.copy_directory(self.data_path, zip_path)
            self.updater_service.save_directory_zip(zip_path, backup_package)
            self.updater_service.test_zip_file(backup_package_zip)
            self._clean_backups()

            logger.info("Loaders backup successfully created!")
        except Exception as _:
            logger.exception("Error creating loaders backup")
            raise ErrorCreatingBackup()

    def _clean_backups(self):
        # type: () -> None
        
        list_of_files = os.listdir(self.backups_path)
        
        while len(list_of_files) > 5:
            full_path = [os.path.join(self.backups_path, x) for x in list_of_files]
            oldest_file = min(full_path, key=os.path.getctime)
            os.remove(oldest_file)
        
            list_of_files = os.listdir(self.backups_path)

    def _delete_content(self, path):
        # type: (str) -> None
    
        try:
            logger.info("Deleting path {}".format(path))
        
            self.updater_service.delete_directory(path)
        
            logger.info("Path deleted")
        except Exception as _:
            logger.exception("Error deleting path")
            raise ErrorDeletingContent()
        
    def _get_new_loaders(self):
        # type: () -> None
        
        try:
            logger.info("Extracting loaders in data path")
            
            self.updater_service.create_dir(self.data_path)
            zip_path = os.path.join(self.downloads_path, self.loaders_zip)
            self.updater_service.extract_zip(zip_path, self.data_path)
            
            logger.info("Loaders extracted in data path")
        except Exception as _:
            logger.exception("Error extracting loaders to data path")
            raise ErrorExtractingLoaders()
        
    def _recover_databases(self):
        # type: () -> None
    
        try:
            logger.info("Recovering databases")

            databases_path = os.path.join(self.server_path, "databases")
            work_path_databases = os.path.join(self.work_path, self.databases_relative_path)
            self.updater_service.copy_directory(work_path_databases, databases_path)
        
            logger.info("Databases recovered")
        except Exception as _:
            logger.exception("Error recovering databases")
            raise ErrorRecoveringDatabases()

    def _update_payments(self):
        # type () -> None

        try:
            logger.info("Updating Payments")
            
            payments_json = open(self.payments_json, "r")
            payments = json.loads(payments_json.read())
            
            all_payments = []
            for payment in payments:
                payment_id = payment.get("id", 0)
                name = payment.get("name", "").encode('utf-8').strip()
                currency = payment.get("tenderCurrency", "BRL")
                change_limit = payment.get("changeLimit", 0)
                electronic_type = payment.get("electronicType", 0)
                open_drawer = payment.get("openDrawer", 0)
                parent_id = payment.get("parentId", None)
    
                payment = Payment(payment_id, name, currency, change_limit, electronic_type, open_drawer, parent_id)
                all_payments.append(payment)
    
            product_db = os.path.join(self.databases_path, "product.db")
            self.pos_repository.delete_all_payments(product_db)
            self.pos_repository.insert_payments(product_db, all_payments)

            logger.info("Payments updated")
        except Exception as _:
            logger.exception("Error inserting payments on database")
            raise ErrorUpdatingDatabases()
        
    def _rollback(self):
        # type: () -> None

        logger.info("Starting rollback")
        
        retries = 0
        max_retries = 2
        
        while True:
            try:
                self._delete_content(self.data_path)
                self._rename_path(self.renamed_data_path, self.data_path)
            except Exception as _:
                logger.exception("Error while executing rollback")
                if retries == max_retries:
                    raise RollbackError()
                
                retries += 1
                continue

            logger.info("Rollback finished")
            break

    def _rename_path(self, path, renamed_path):
        # type: (str, str) -> None
    
        try:
            logger.info("Renaming folder from {} to {}".format(path, renamed_path))
        
            self.updater_service.rename_folder(path, renamed_path)
        
            logger.info("Data folder renamed!")
        except Exception as _:
            logger.exception("Error renaming data folder")
            raise ErrorDeletingContent()
        
