from threading import Lock

from application.model import UpdateType, UserUpdateData
from application.model.configuration import Configurations
from application.model.customexception import ErrorApplyingUpdate, NotInsideUpdateWindow, NotExpectedException, \
    DisabledFunctionality
from application.repository.api import UserUpdaterAPIRepository
from application.repository.pos import UserUpdaterPOSRepository
from application.util import LoggerUtil, ValidationUtil
from typing import Union, Dict, Optional

logger = LoggerUtil.get_logger_name(__name__)


class UserUpdaterInteractor(object):
    def __init__(self, configs, working_on_update, api_repository, pos_repository, enabled):
        # type: (Configurations, Lock, Optional[UserUpdaterAPIRepository], UserUpdaterPOSRepository, bool) -> None

        self.logger = logger
        self.configs = configs
        self.update_type = UpdateType.user
        self.local_configs = configs.updaters[self.update_type.name]
        self.api_repository = api_repository
        self.pos_repository = pos_repository
        self.working_on_update = working_on_update
        self.enabled = enabled

        self.users_update_data = dict()  # type: Union[Dict[int, UserUpdateData], None]

    def update_users(self, ignore_update_window):
        # type: (bool) -> None
        
        if not self.enabled:
            raise DisabledFunctionality()
        
        try:
            with self.working_on_update:
                self.logger.info("Updating Users")
        
                if self.pos_repository.some_update_already_applied() and not ignore_update_window:
                    self._check_update_window()
                    
                self._get_users_update_data()
                self._apply_update()
        
                self.logger.info("Update fully concluded with success!")
        except NotInsideUpdateWindow as _:
            self.logger.info("Sleeping until enter the update window")
            raise
        except (NotExpectedException, Exception) as _:
            self.logger.exception("Not expected exception on user update")
            raise

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

    def _get_users_update_data(self):
        # type: () -> None

        self.logger.info("Trying to obtain employees data...")
        
        received_employee_data = self.api_repository.get_employees_data()

        for user in received_employee_data:
            user_data = UserUpdateData()
            
            user_data.user_id = int(user.get("pos-user-id"))
            user_data.long_name = user.get("name").encode("utf-8")
            user_data.password = user.get("pos-password")
            user_data.level = user.get("pos-access-level").get("code")
            user_data.start_date = user.get("from-dt")
            user_data.end_date = user.get("to-dt")
            user_data.pay_rate = user.get("pay-rate-amount")
            user_data.fill_user_status()
            
            self.users_update_data[user_data.user_id] = user_data

        self.logger.info("Package successfully obtained!")

    def _apply_update(self):
        # type: () -> None

        try:
            self.logger.info("Applying update on database...")
    
            self.pos_repository.update_users(self.users_update_data)
            
            last_user_update_id = self.pos_repository.get_last_user_update_id()
            self.pos_repository.insert_new_user_update(last_user_update_id + 1, "Users")
            
            self.logger.info("Package successfully applied!")
        except Exception as ex:
            self.logger.exception("Error applying update")
            raise ErrorApplyingUpdate(ex)
