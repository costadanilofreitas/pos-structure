# -*- coding: utf-8 -*-

import logging

from application.model.configuration import Configurations
from application.model.customexception import ConfigurationReaderException
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

            self.configs.supported_benefit_appliers = self._get_config("SupportedBenefitAppliers", array=True) or []
            self.configs.supported_benefit_appliers = [str(x) for x in self.configs.supported_benefit_appliers]
            self.configs.retry_frequency = int(self._get_config("RetryFrequency") or 30)
            self.configs.max_retry_quantity = int(self._get_config("MaxRetryQuantity") or 99)
            self.configs.retry_min_time_to_try_again = int(self._get_config("RetryMinTimeToTryAgain") or 300)
            
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
