# -*- coding: utf-8 -*-

from datetime import datetime

from application.model import UpdateType
from application.model.configuration import Configurations, CatalogConfigurations, MediaConfigurations, \
    UserConfigurations
from application.model.configuration import LoaderConfigurations
from application.model.customexception import ConfigurationReaderException
from cfgtools import read, Configuration
from mbcontextmessagehandler import MbContextMessageBus
from messagebus import Message, DataType
from msgbus import TK_SYS_NAK, TK_STORECFG_GET
from systools import sys_parsefilepath
from ._ConfiguratorReader import ConfiguratorReader


class Configurator(object):
    
    def __init__(self):
        self.configs = Configurations()
        
        self.window_start_time = "Window.StartTime"
        self.window_end_time = "Window.EndTime"
    
    def get_loader_configurations(self, loader_cfg):
        # type: (str) -> None
        
        reader = read(loader_cfg)
        
        self.configs.service_name = str(reader.find_value("Identification.ComponentName"))
        
        def _get_config_path(key):
            return self.configs.service_name + "." + key
        
        self.configs.persistence_name = str(reader.find_value(_get_config_path("PersistenceName")))
        self.configs.required_services = "|".join(reader.find_values(_get_config_path("RequiredServices")))
        self.configs.backup_directory = str(sys_parsefilepath(reader.find_value(_get_config_path("BackupDirectory"))))
        
        local_store_id = reader.find_value(_get_config_path("StoreId"))
        self.configs.store_id = str(local_store_id) if local_store_id else None
        
        self.configs.updaters = {}
        
        self._get_catalog_configurations(reader)
        self._get_media_configurations(reader)
        self._get_user_configurations(loader_cfg)
        self._get_loader_configurations(loader_cfg)
        
        for manager in self.configs.updaters:
            config = self.configs.updaters[manager]
            if config.enabled and config.name not in UpdateType.list_names():
                raise ConfigurationReaderException("Not supported manager: {}".format(config.name))
    
    def get_base_url(self, message_bus):
        # type: (MbContextMessageBus) -> None
        
        self.configs.base_url = self.read_sw_config(message_bus, "BackOffice.ServerURL") + "/pump"
    
    def get_api_key(self, message_bus):
        # type: (MbContextMessageBus) -> None
        
        self.configs.api_key = self.read_sw_config(message_bus, "BackOffice.ApiKey")
    
    def get_store_id(self, message_bus):
        # type: (MbContextMessageBus) -> None
        
        self.configs.store_id = self.read_sw_config(message_bus, "Store.Id")
    
    @staticmethod
    def read_sw_config(message_bus, key):
        # type: (MbContextMessageBus, str) -> Configurations
        
        message = Message(TK_STORECFG_GET, data_type=DataType.param, data=key)
        msg = message_bus.send_message("StoreWideConfig", message)
        if msg.token == TK_SYS_NAK:
            raise ConfigurationReaderException("Unable to get Store Wide Configuration: {}".format(key))
        return str(msg.data)
    
    def _get_catalog_configurations(self, reader):
        # type: (Configuration) -> None
        
        catalog = CatalogConfigurations()
        manager_name = "Catalog"
        
        def _get_config(param):
            return reader.find_value(self.configs.service_name + "." + manager_name + "." + param)
        
        catalog.enabled = (_get_config("Enabled") or "false").lower() == "true"
        
        catalog.name = manager_name.lower()
        catalog.active_frequency = int(_get_config("ActiveFrequency"))
        
        catalog.window.start_time = datetime.strptime(_get_config(self.window_start_time), "%H:%M:%S").time()
        catalog.window.end_time = datetime.strptime(_get_config(self.window_end_time), "%H:%M:%S").time()
        
        catalog.endpoints.get_latest_version = str(_get_config("Endpoints.getLatestVersion"))
        catalog.endpoints.download = str(_get_config("Endpoints.download"))
        catalog.endpoints.update_to = str(_get_config("Endpoints.updateTo"))
        
        self.configs.updaters[catalog.name] = catalog
    
    def _get_media_configurations(self, reader):
        # type: (Configuration) -> None
        
        media = MediaConfigurations()
        manager_name = "Media"
        
        def _get_config(param):
            return reader.find_value(self.configs.service_name + "." + manager_name + "." + param)
        
        media.enabled = (_get_config("Enabled") or "false").lower() == "true"
        
        media.name = manager_name.lower()
        media.active_frequency = int(_get_config("ActiveFrequency"))
        
        media.images_directory = str(sys_parsefilepath(_get_config("ImagesDirectory")))
        
        media.window.start_time = datetime.strptime(_get_config(self.window_start_time), "%H:%M:%S").time()
        media.window.end_time = datetime.strptime(_get_config(self.window_end_time), "%H:%M:%S").time()
        
        media.endpoints.get_download_image_permission = str(_get_config("Endpoints.getDownloadImagePermission"))
        
        self.configs.updaters[media.name] = media
    
    def _get_user_configurations(self, loader_cfg):
        # type: (Configuration) -> None
        
        user = UserConfigurations()
        manager_name = "User"
        configurator_reader = ConfiguratorReader(loader_cfg, self.configs.service_name, manager_name)
        
        user.enabled = (configurator_reader.get_configuration("Enabled") or "false").lower() == "true"
        
        user.name = manager_name.lower()
        user.active_frequency = (configurator_reader.get_configuration("ActiveFrequency") or "0")

        start_time = configurator_reader.get_configuration(self.window_start_time)
        user.window.start_time = datetime.strptime(start_time, "%H:%M:%S").time()
        end_time = configurator_reader.get_configuration(self.window_end_time)
        user.window.end_time = datetime.strptime(end_time, "%H:%M:%S").time()

        user.endpoints.employee = configurator_reader.get_configuration("Endpoints.employee")
        
        self.configs.updaters[user.name] = user

    def _get_loader_configurations(self, loader_cfg):
        # type: (Configuration) -> None
    
        manager_name = "Loader"
        
        loader = LoaderConfigurations()
        loader.name = manager_name.lower()
        configurator_reader = ConfiguratorReader(loader_cfg, self.configs.service_name, manager_name)
        
        loader.enabled = (configurator_reader.get_configuration("Enabled") or "false").lower() == "true"
        loader.active_frequency = (configurator_reader.get_configuration("ActiveFrequency") or "0")

        start_time = configurator_reader.get_configuration(self.window_start_time)
        loader.window.start_time = datetime.strptime(start_time, "%H:%M:%S").time()
        end_time = configurator_reader.get_configuration(self.window_end_time)
        loader.window.end_time = datetime.strptime(end_time, "%H:%M:%S").time()

        loader.endpoints.download_loaders = configurator_reader.get_configuration("Endpoints.loaders")
    
        self.configs.updaters[loader.name] = loader
