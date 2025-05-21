from application.interactor import CatalogUpdaterInteractor
from application.model import BaseThread, UpdateType, CatalogUpdateData, UpdateStep, UpdateStatus
from application.model.configuration import Configurations
from application.model.customexception import NotInsideUpdateWindow, NoUpdateFound, DisabledFunctionality
from application.repository.api import CatalogUpdaterAPIRepository
from application.repository.pos import CatalogUpdaterPOSRepository
from application.service import UpdaterService
from application.util import LoggerUtil, ValidationUtil

logger = LoggerUtil.get_logger_name(__name__)


class CatalogUpdaterManager(BaseThread):
    def __init__(self, configs, catalog_updater_interactor, api_repository, pos_repository, updater_service):
        # type: (Configurations, CatalogUpdaterInteractor, CatalogUpdaterAPIRepository, CatalogUpdaterPOSRepository, UpdaterService) -> None # noqa

        super(CatalogUpdaterManager, self).__init__()
        self.configs = configs
        self.update_type = UpdateType.catalog
        self.local_configs = configs.updaters[self.update_type.name]
        self.active_frequency = self.local_configs.active_frequency
        self.interactor = catalog_updater_interactor
        self.api_repository = api_repository
        self.pos_repository = pos_repository
        self.updater_service = updater_service

    def run(self):
        # type: () -> None

        if self.active_frequency == 0:
            logger.info("Auto-update thread disabled. Stopping manager...")
            self.stop()
            return
        
        logger.info("{} update thread manager started".format(self.update_type.name.upper()))

        while self.running:
            self._download_pending_version()
            self._apply_version()
            self._notify_update()
            
            self.sleep(self.active_frequency)

    def _download_pending_version(self):
        # type: () -> None
        
        try:
            self.updater_service.download_pending_version()
        except Exception as _:
            logger.exception("Error on automatically download version")
            
    def _apply_version(self):
        # type: () -> None
        
        try:
            if self.pos_repository.some_update_already_applied():
                self._check_update_window()
                
            self.interactor.apply_update()
        except (NotInsideUpdateWindow, NoUpdateFound) as _:
            pass
        except DisabledFunctionality as _:
            self.logger.info("Disabled update catalog functionality")
        except Exception as _:
            logger.exception("Error on automatically apply version")

    def _notify_update(self):
        # type: () -> None
    
        try:
            update_id = self.pos_repository.get_pending_update_to_notify()
            if update_id:
                logger.info("Notifying update {}".format(update_id))
                self.api_repository.notify_applied_update(update_id)
                self.pos_repository.update_step(update_id, UpdateStep.notify)
                self.pos_repository.update_status(update_id, UpdateStatus.applied)
                logger.info("Update {} successfully notified!".format(update_id))
            else:
                logger.info("There is no update to notify")
        except Exception as _:
            logger.exception("Error on automatically notify update")
            
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
