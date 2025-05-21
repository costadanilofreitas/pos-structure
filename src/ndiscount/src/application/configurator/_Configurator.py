# -*- coding: utf-8 -*-

import logging

from application.model import ConfigurationReaderException, Configurations
from cfgtools import read
from helper import config_logger
from typing import Optional


class Configurator(object):

    def __init__(self, loader_path):
        # type: (str) -> None

        self.loader_path = loader_path
        self.reader = read(self.loader_path)
        self.configs = Configurations()

    def read_loader_configurations(self):
        # type: () -> None

        try:
            self.configs.service_name = str(self.reader.find_value("Identification.ComponentName"))
            self.configs.required_services = "|".join(self._get_config("RequiredServices", array=True) or [])
            self.configs.persistence_name = str(self._get_config("PersistenceName") or "")
            self.configs.promotional_tender_type_id = self._get_config("PromotionalTenderTypeId") or ""

        except Exception as ex:
            raise ConfigurationReaderException(ex)

    def configure_logger(self):
        # type: () -> None

        config_logger(self.loader_path, self.configs.service_name)
        self.configs.logger = logging.getLogger(self.configs.service_name)

    def _get_config(self, key, array=False):
        # type: (str, Optional[bool]) -> str

        path = self.configs.service_name + "." + key
        return self.reader.find_values(path) if array else self.reader.find_value(path)
