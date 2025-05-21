import json
from logging import Logger

import requests
from application.model import UpdateType
from application.model.configuration import Configurations
from application.model.customexception import \
    ErrorRetrievingPendingUpdate, \
    ErrorDownloadingUpdatePackage, \
    ErrorNotifyingAppliedUpdate
from helper import retry, json_serialize
from requests import Response


class CatalogUpdaterAPIRepository(object):

    def __init__(self, logger, configs):
        # type: (Logger, Configurations) -> None

        self.logger = logger
        self.configs = configs
        self.update_type = UpdateType.catalog
        self.local_configs = configs.updaters[self.update_type.name]

    def retrieve_pending_update(self):
        # type: () -> str

        url = self._get_latest_version_url()
        headers = self._get_app_json_headers()

        response = retry(
                logger=self.logger,
                method_name="retrieve_pending_update",
                n=3,
                sleep_seconds=5,
                trying_to_do=lambda: requests.request("GET", url=url, headers=headers, timeout=60),
                is_success=lambda resp: resp.status_code == 200,
                success=lambda resp: resp,
                failed=lambda resp: self.logger.error("Error getting latest version: {}".format(json_serialize(resp)))
        )

        if response is None:
            raise ErrorRetrievingPendingUpdate()

        return json.loads(response.content)

    def get_latest_package(self):
        # type: () -> Response

        url = self._get_download_url()
        headers = self._get_app_zip_headers()

        response = retry(
                logger=self.logger,
                method_name="get_latest_package",
                n=3,
                sleep_seconds=5,
                trying_to_do=lambda: requests.get(url=url, headers=headers, stream=True, timeout=120),
                is_success=lambda resp: resp.status_code == 302,
                success=lambda resp: resp,
                failed=lambda resp: self.logger.error("Error downloading update package: {}".format(json_serialize(resp)))
        )

        if response is None:
            raise ErrorDownloadingUpdatePackage()

        download_url = json.loads(response.content)["location"]
        self.logger.info("New package download URL: {}".format(download_url))
        
        package = requests.get(download_url, allow_redirects=True)
        
        self.logger.info("Package successfully downloaded!")
        return package

    def notify_applied_update(self, update_id):
        # type: (int) -> None

        url = self._get_updated_to_url(update_id)
        headers = self._get_app_json_headers()

        response = retry(
                logger=self.logger,
                method_name="notify_applied_update",
                n=3,
                sleep_seconds=5,
                trying_to_do=lambda: requests.request("POST", url=url, headers=headers, timeout=120),
                is_success=lambda resp: resp.status_code == 204,
                success=lambda resp: resp,
                failed=lambda resp: self.logger.error("Error notifying applied update: {}".format(json_serialize(resp)))
        )

        if response is None:
            raise ErrorNotifyingAppliedUpdate()

    def _get_app_json_headers(self):
        # type: () -> str

        return {"X-Api-Key": self.configs.api_key,
                "Content-type": "application/json"}

    def _get_app_zip_headers(self):
        # type: () -> str

        return {"X-Api-Key": self.configs.api_key,
                "Content-type": "application/zip"}

    def _get_latest_version_url(self):
        # type: () -> str

        end_point_url = self.local_configs.endpoints.get_latest_version.format(storeId=self.configs.store_id)
        return self.configs.base_url + end_point_url

    def _get_download_url(self):
        # type: () -> str

        end_point_url = self.local_configs.endpoints.download.format(storeId=self.configs.store_id)
        return self.configs.base_url + end_point_url

    def _get_updated_to_url(self, updated_id):
        # type: (int) -> str

        end_point_url = self.local_configs.endpoints.update_to.format(storeId=self.configs.store_id,
                                                                      versionNumber=str(updated_id))
        return self.configs.base_url + end_point_url
