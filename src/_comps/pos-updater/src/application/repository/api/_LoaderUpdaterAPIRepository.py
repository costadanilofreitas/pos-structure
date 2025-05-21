from logging import Logger

import requests
from application.model import UpdateType
from application.model.configuration import Configurations
from application.model.customexception import ErrorDownloadingLoaders
from helper import retry, json_serialize
from requests import Response


class LoaderUpdaterAPIRepository(object):

    def __init__(self, logger, configs):
        # type: (Logger, Configurations) -> None

        self.logger = logger
        self.configs = configs
        self.update_type = UpdateType.loader
        self.local_configs = configs.updaters[self.update_type.name]

    def download_loaders(self, file_path):
        # type: () -> str

        url = self._get_download_url()
        headers = self._get_zip_headers()

        response = retry(
                logger=self.logger,
                method_name="download_loaders",
                n=3,
                sleep_seconds=5,
                trying_to_do=lambda: requests.request("GET", url=url, headers=headers, timeout=60),
                is_success=lambda resp: resp.status_code == 302,
                success=lambda resp: resp,
                failed=lambda resp: self.logger.error("Error downloading loaders: {}".format(json_serialize(resp)))
        )

        if response is None:
            raise ErrorDownloadingLoaders()

        package = self._download_package(response.content.strip('\"'))
        self._save_package(file_path, package)

    @staticmethod
    def _save_package(file_path, package):
        # type: (str, Response) -> None
        
        with open(file_path, "wb") as zip_object:
            for chunk in package.iter_content(chunk_size=128):
                zip_object.write(chunk)

    @staticmethod
    def _download_package(download_url):
        # type: (str) -> Response
        
        package = requests.get(download_url, allow_redirects=True)
        return package

    def _get_download_url(self):
        # type: () -> str

        end_point_url = self.local_configs.endpoints.download_loaders.format(storeId=self.configs.store_id)
        return self.configs.base_url + end_point_url

    def _get_zip_headers(self):
        # type: () -> str

        return {"X-Api-Key": self.configs.api_key,
                "Content-type": "application/zip"}
