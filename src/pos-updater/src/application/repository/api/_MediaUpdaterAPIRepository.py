import json

import requests
from application.model import UpdateType
from application.model.configuration import Configurations
from application.model.customexception import ErrorRetrievingPendingUpdate
from helper import retry, json_serialize
from requests import Response
from application.util import LoggerUtil

NONE_RESPONSE_ERROR = "Could not obtain the request response content"
logger = LoggerUtil.get_logger_name(__name__)


class MediaUpdaterAPIRepository(object):
    def __init__(self, configs):
        # type: (Configurations) -> None

        self.logger = logger
        self.configs = configs
        self.update_type = UpdateType.media
        self.local_configs = configs.updaters[self.update_type.name]

    def get_images_permissions(self, hashes_to_get_permission):
        # type: (str) -> str
        
        self.logger.info("Obtaining images permissions...")
        
        url = self._get_download_image_permission_url()
        headers = self._get_app_json_headers()
        data = json_serialize(hashes_to_get_permission)
    
        response = retry(
                logger=self.logger,
                method_name="get_images_permissions",
                n=3,
                sleep_seconds=5,
                trying_to_do=lambda: requests.request("POST", url=url, headers=headers, data=data, timeout=60),
                is_success=lambda resp: resp.status_code == 200,
                success=lambda resp: resp,
                failed=lambda resp: self.logger.error("Error getting images permissions: {}"
                                                      .format(json_serialize(resp)))
        )
    
        if response is None:
            raise ErrorRetrievingPendingUpdate(NONE_RESPONSE_ERROR)

        self.logger.info("Permissions obtained!")
    
        return json.loads(response.content)
    
    @staticmethod
    def download_image(download_url):
        # type: (str) -> Response
        
        return requests.get(download_url, allow_redirects=True)

    def _get_app_json_headers(self):
        # type: () -> str
    
        return {"X-Api-Key": self.configs.api_key,
                "Content-type": "application/json"}

    def _get_download_image_permission_url(self):
        # type: () -> str
    
        end_point_url = self.local_configs.endpoints.get_download_image_permission
        return self.configs.base_url + end_point_url
