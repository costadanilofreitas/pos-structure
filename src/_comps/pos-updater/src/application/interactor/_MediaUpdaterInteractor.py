import json
import os
from datetime import datetime
from threading import Lock

import pytz
from application.model import UpdateType, MediaUpdateData
from application.model.configuration import Configurations
from application.model.customexception import ErrorRetrievingPendingUpdate, ErrorApplyingUpdate, \
    HasNoProductsImagesToDownload, NoUpdateFound, NotExpectedException, DisabledFunctionality
from application.repository.api import MediaUpdaterAPIRepository
from application.repository.pos import MediaUpdaterPOSRepository
from iso8601 import iso8601
from requests import Response
from typing import Dict, List
from application.util import LoggerUtil

logger = LoggerUtil.get_logger_name(__name__)


class MediaUpdaterInteractor(object):
    def __init__(self, configs, working_on_update, api_repository, pos_repository, enabled):
        # type: (Configurations, Lock, MediaUpdaterAPIRepository, MediaUpdaterPOSRepository, bool) -> None

        self.logger = logger
        self.configs = configs
        self.update_type = UpdateType.media
        self.local_configs = configs.updaters[self.update_type.name]
        self.working_on_update = working_on_update
        self.api_repository = api_repository
        self.pos_repository = pos_repository
        self.enabled = enabled

        self.images_path = self.local_configs.images_directory
        self.control_json_path = os.path.join(self.images_path, "imagesHashes.json")
        
        if not os.path.exists(self.images_path):
            os.makedirs(self.images_path)

    def update_media(self):
        # type: () -> None
        
        if not self.enabled:
            raise DisabledFunctionality
        
        try:
            with self.working_on_update:
                self.logger.info("Trying to update media...")
        
                images_hashes_from_database = self.pos_repository.get_images_hashes_from_database()
                images_hashes_from_json = self._get_images_hashes_from_json()
        
                images_to_download = self._filter_images_to_download(images_hashes_from_database, images_hashes_from_json)
        
                if not images_to_download:
                    raise HasNoProductsImagesToDownload()
        
                images_to_download = self._format_images_to_update_data(images_to_download)
                self._get_images_permissions(images_to_download)
                self._download_and_store_images(images_to_download)
                self._remove_old_images_from_path(images_hashes_from_database, images_hashes_from_json)
                self._update_images_hashes_json(images_hashes_from_database, images_hashes_from_json, images_to_download)
        
                for image in images_to_download:
                    if not image.downloaded:
                        raise ErrorApplyingUpdate()
    
            self.logger.info("Media update fully concluded!")
        except NoUpdateFound as _:
            self.logger.info("No pending updates found")
            raise
        except HasNoProductsImagesToDownload as _:
            self.logger.info("Has not products to download images")
            raise
        except ErrorRetrievingPendingUpdate as _:
            self.logger.exception("Error retrieving pending update")
            raise
        except ErrorApplyingUpdate:
            self.logger.error("Error doing update")
            raise
        except (NotExpectedException, Exception) as _:
            self.logger.exception("Not expected exception on media update")
            raise

    def _remove_old_images_from_path(self, images_hashes_from_database, images_hashes_from_json):
        # type: (Dict, Dict) -> None
        
        self.logger.info("Cleaning useless images from images path...")
        
        for product_code in images_hashes_from_json.keys():
            if product_code not in images_hashes_from_database:
                product_image_name = self._format_product_image_name(product_code)
                product_image_path = self._get_image_path(product_image_name)
                if os.path.isfile(product_image_path):
                    os.remove(product_image_path)

    def _update_images_hashes_json(self, images_hashes_from_database, images_hashes_from_json, images_to_update):
        # type: (Dict, Dict, List[MediaUpdateData]) -> None
        
        self.logger.info("Updating [imagesHashes.json]...")
        
        for image in images_to_update:
            if image.downloaded:
                images_hashes_from_json[image.product_code] = image.image_hash
            
        for product_code in images_hashes_from_json.keys():
            if product_code not in images_hashes_from_database:
                del images_hashes_from_json[product_code]
                
        with open(self.control_json_path, "w") as json_file:
            json.dump(images_hashes_from_json, json_file)

    def _format_images_to_update_data(self, images_to_download):
        # type: (Dict) -> List[MediaUpdateData]
        
        formatted_images_to_download = list()
        for product_code in images_to_download:
            update_data = MediaUpdateData()
            update_data.product_code = product_code
            update_data.image_hash = images_to_download[product_code]
        
            formatted_images_to_download.append(update_data)

        products_to_download = [x.product_code for x in formatted_images_to_download]
        self.logger.info("Trying to obtain images for products: {}".format(products_to_download))
        
        return formatted_images_to_download

    def _get_images_hashes_from_json(self):
        # type: () -> Dict
        
        images_hashes_from_json = dict()
        if os.path.isfile(self.control_json_path):
            with open(self.control_json_path) as json_file:
                images_hashes_from_json = json.load(json_file)
        
        return images_hashes_from_json

    @staticmethod
    def _filter_images_to_download(images_hashes_from_database, images_hashes_from_json):
        # type: (Dict, Dict) -> Dict
        
        product_that_we_need_to_download = {}
        for product_code in images_hashes_from_database:
            database_hash = images_hashes_from_database[product_code]
            if product_code not in images_hashes_from_json or database_hash != images_hashes_from_json[product_code]:
                product_that_we_need_to_download[product_code] = database_hash
        
        return product_that_we_need_to_download
    
    def _get_images_permissions(self, images_to_download):
        # type: (List[MediaUpdateData]) -> None
    
        try:
            hashes_to_get_permission = []
            for image_to_download in images_to_download:
                hashes_to_get_permission.append(image_to_download.image_hash)
                
            images_permissions = self.api_repository.get_images_permissions(hashes_to_get_permission)

            for image_permission in images_permissions:
                obtained_image_hash = image_permission.get("imageHash")
                for image_to_download in images_to_download:
                    if image_to_download.image_hash == obtained_image_hash:
                        image_to_download.link_to_download = image_permission.get("link")
                        image_to_download.expiration_date = iso8601.parse_date(image_permission.get("expirationDate"))
                        
        except Exception as ex:
            raise ErrorRetrievingPendingUpdate(ex)

    def _download_and_store_images(self, images_to_download):
        # type: (List[MediaUpdateData]) -> None
        
        for image_to_download in images_to_download:
            now = _get_utc_now()
            if image_to_download.expiration_date and now > image_to_download.expiration_date:
                self.logger.error("Expiration date reached for product: {}".format(image_to_download.product_code))
                continue
                
            if not image_to_download.link_to_download:
                self.logger.error("Image has no link to download: {}".format(image_to_download.product_code))
                continue
            
            package = self.api_repository.download_image(image_to_download.link_to_download)
            if not package.ok:
                self.logger.error("Could not download image for product: {}".format(image_to_download.product_code))
                continue
                
            product_image_name = self._format_product_image_name(image_to_download.product_code)
            product_image_path = self._get_image_path(product_image_name)

            self._store_image(product_image_path, package)

            image_to_download.downloaded = True
            
            self.logger.info("Image downloaded and stored for product: {}".format(image_to_download.product_code))

    def _get_image_path(self, prt_image_name):
        # type: (str) -> str
        
        return os.path.join(self.images_path, prt_image_name)

    @staticmethod
    def _format_product_image_name(product_code):
        # type: (str) -> str
        
        return "PRT" + product_code.zfill(8) + ".png"
    
    @staticmethod
    def _store_image(image_path, package):
        # type: (str, Response) -> None
        
        with open(image_path, "wb") as image_file:
            for chunk in package.iter_content(chunk_size=128):
                image_file.write(chunk)


def _get_utc_now():
    # type: () -> datetime
    
    return pytz.UTC.localize(datetime.utcnow())
