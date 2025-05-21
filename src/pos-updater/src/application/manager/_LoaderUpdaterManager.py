from application.interactor import UserUpdaterInteractor
from application.model import BaseThread, UpdateType
from application.model.configuration import Configurations
from application.util import LoggerUtil

logger = LoggerUtil.get_logger_name(__name__)


class LoaderUpdaterManager(BaseThread):
    def __init__(self, configs, user_updater_interactor):
        # type: (Configurations, UserUpdaterInteractor) -> None

        super(LoaderUpdaterManager, self).__init__()
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

        sleep_time = self.active_frequency
        while self.running:
            try:
                self.interactor.update_loaders(False)
            except Exception as _: # noqa
                self.logger.exception("Not expected exception on loader update")

            self.sleep(int(sleep_time))
