from datetime import datetime, date

from application.interactor import MediaUpdaterInteractor
from application.model import BaseThread, UpdateType
from application.model.configuration import Configurations
from application.model.customexception import NotInsideUpdateWindow, NoUpdateFound, NotExpectedException, \
    ErrorRetrievingPendingUpdate, HasNoProductsImagesToDownload, DisabledFunctionality
from application.util import LoggerUtil

logger = LoggerUtil.get_logger_name(__name__)


class MediaUpdaterManager(BaseThread):
    def __init__(self, configs, media_updater_interactor):
        # type: (Configurations, MediaUpdaterInteractor) -> None

        super(MediaUpdaterManager, self).__init__()
        self.logger = logger
        self.configs = configs
        self.update_type = UpdateType.media
        self.local_configs = configs.updaters[self.update_type.name]
        self.active_frequency = self.local_configs.active_frequency
        self.interactor = media_updater_interactor

    def run(self):
        # type: () -> None
        
        if self.active_frequency == 0:
            self.logger.info("Auto-update thread disabled. Stopping manager...")
            self.stop()
            return

        self.logger.info("{} update thread manager started".format(self.update_type.name.upper()))
        self._update_media()

    def _update_media(self):
        while self.running:
            sleep_time = self.active_frequency
            try:
                self.interactor.update_media()
            except NoUpdateFound as _:
                self.logger.info("No pending updates found")
            except HasNoProductsImagesToDownload as _:
                self.logger.info("Has not products to download images")
            except NotInsideUpdateWindow as _:
                self.logger.info("Sleeping until enter the update window")
                sleep_time = self._get_remaining_seconds_to_update_window()
            except ErrorRetrievingPendingUpdate as _:
                self.logger.exception("Error retrieving pending update")
            except DisabledFunctionality as _:
                self.logger.info("Disabled update media functionality")
            except (NotExpectedException, Exception) as _:
                self.logger.exception("Not expected exception on catalog update")
            finally:
                self.sleep(sleep_time)

    def _get_remaining_seconds_to_update_window(self):
        start_time = datetime.combine(date.today(), self.local_configs.window.start_time)
        now = datetime.now()
        return (start_time - now).seconds
