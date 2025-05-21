import requests
from application.model import UpdateType
from application.model.configuration import Configurations
from application.model.customexception import ErrorRetrievingUsers
from helper import retry, json_serialize
from typing import Dict
from application.util import LoggerUtil

logger = LoggerUtil.get_logger_name(__name__)


class UserUpdaterAPIRepository(object):
    def __init__(self, configs):
        # type: (Configurations) -> None

        self.logger = logger
        self.configs = configs
        self.update_type = UpdateType.user
        self.local_configs = configs.updaters[self.update_type.name]

    def get_employees_data(self):
        # type: () -> Dict
        
        self.logger.info("Obtaining users data...")
        
        url = self._get_employee_url()
        headers = self._get_app_json_headers()
    
        response = retry(
                logger=self.logger,
                method_name="get_employees_data",
                n=3,
                sleep_seconds=5,
                trying_to_do=lambda: requests.request("GET", url=url, headers=headers, timeout=60),
                is_success=lambda resp: resp.status_code == 200,
                success=lambda resp: resp,
                failed=lambda resp: self.logger.error("Error getting employees data: {}".format(json_serialize(resp)))
        )
    
        if response is None:
            raise ErrorRetrievingUsers()

        self.logger.info("Employees data successfully obtained!")
    
        return response.json()

    def _get_app_json_headers(self):
        # type: () -> str
    
        return {"X-Api-Key": self.configs.api_key,
                "Content-type": "application/json"}

    def _get_employee_url(self):
        # type: () -> str
    
        end_point_url = self.local_configs.endpoints.employee.format(storeId=self.configs.store_id)
        return self.configs.base_url + end_point_url
