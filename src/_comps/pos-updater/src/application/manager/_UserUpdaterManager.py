from datetime import datetime, date

from application.interactor import UserUpdaterInteractor
from application.model import BaseThread, UpdateType
from application.model.configuration import Configurations
from application.model.customexception import NotInsideUpdateWindow, NotExpectedException, DisabledFunctionality
from application.util import LoggerUtil

logger = LoggerUtil.get_logger_name(__name__)


class UserUpdaterManager(BaseThread):
    def __init__(self, configs, user_updater_interactor):
        # type: (Configurations, UserUpdaterInteractor) -> None

        super(UserUpdaterManager, self).__init__()
        self.logger = logger
        self.configs = configs
        self.update_type = UpdateType.user
        self.local_configs = configs.updaters[self.update_type.name]
        self.active_frequency = self.local_configs.active_frequency
        self.interactor = user_updater_interactor

    def run(self):
        # type: () -> None
        
        if self.active_frequency == 0:
            self.logger.info("Auto-update thread disabled. Stopping manager...")
            self.stop()
            return
        
        self.logger.info("{} update thread manager started".format(self.update_type.name.upper()))

        while self.running:
            sleep_time = self.active_frequency
            
            try:
                self.interactor.update_users(False)
            except NotInsideUpdateWindow as _:
                self.logger.info("Sleeping until enter the update window")
                sleep_time = self._get_remaining_seconds_to_update_window()
            except DisabledFunctionality as _:
                self.logger.info("Disabled update users functionality")
            except (NotExpectedException, Exception) as _:
                self.logger.exception("Not expected exception on catalog update")
            finally:
                self.sleep(sleep_time)

    def _get_remaining_seconds_to_update_window(self):
        start_time = datetime.combine(date.today(), self.local_configs.window.start_time)
        now = datetime.now()
        return (start_time - now).seconds
