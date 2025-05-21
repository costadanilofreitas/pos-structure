# -*- coding: utf-8 -*-

import logging

from mbcontextmessagehandler import MbContextMessageBus
from messagebus import Message, DataType
from msgbus import TK_STORECFG_GET, TK_SYS_NAK
from typing import Optional

from application.model.customexception import ConfigurationReaderException
from application.model.configuration import Configurations
from cfgtools import read
from helper import config_logger


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
            self.configs.persistence_name = str(self._get_config("PersistenceName") or "")
            self.configs.required_services = "|".join(self._get_config("RequiredServices", array=True) or [])
            self.configs.base_url = str(self._get_config("BaseURL") or "")
            self.configs.api_key = str(self._get_config("ApiKey") or "")
            
            self.configs.endpoints.retrieve_loyalty_customer_info = str(self._get_config("EndPoints.RetrieveLoyaltyId") or "")
            self.configs.endpoints.retrieve_benefit = str(self._get_config("EndPoints.RetrieveBenefit") or "")
            self.configs.endpoints.burn_benefit = str(self._get_config("EndPoints.BurnBenefit") or "")
            self.configs.endpoints.unlock_benefit = str(self._get_config("EndPoints.UnlockBenefit") or "")
            
        except Exception as ex:
            raise ConfigurationReaderException(ex)
        
    def configure_logger(self):
        # type: () -> None
        
        config_logger(self.loader_path, self.configs.service_name)
        self.configs.logger = logging.getLogger(self.configs.service_name)

    def get_store_id(self, message_bus):
        # type: (MbContextMessageBus) -> None

        self.configs.store_id = self._read_sw_config(message_bus, "Store.Id")

    @staticmethod
    def _read_sw_config(message_bus, key):
        # type: (MbContextMessageBus, str) -> Configurations

        message = Message(TK_STORECFG_GET, data_type=DataType.param, data=key)
        msg = message_bus.send_message("StoreWideConfig", message)
        if msg.token == TK_SYS_NAK:
            raise ConfigurationReaderException("Unable to get Store Wide Configuration: {}".format(key))
        return str(msg.data)

    def _get_config(self, key, array=False):
        # type: (str, Optional[bool]) -> str

        path = self.configs.service_name + "." + key
        return self.reader.find_values(path) if array else self.reader.find_value(path)
