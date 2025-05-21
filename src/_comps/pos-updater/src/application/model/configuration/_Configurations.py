from application.model.configuration import DefaultManagerConfig, CatalogConfigurations, MediaConfigurations
from application.model.configuration import UserConfigurations
from typing import Dict, Union


class Configurations(object):
    def __init__(self,
                 required_services=None,
                 service_name=None,
                 persistence_name=None,
                 store_id=None,
                 base_url=None,
                 api_key=None,
                 backup_directory=None,
                 updaters=None):
        # type: (str, str, str, str, str, str, str, Dict[str, Union[DefaultManagerConfig, CatalogConfigurations, MediaConfigurations, UserConfigurations]]) -> None # noqa

        self.required_services = required_services
        self.service_name = service_name
        self.persistence_name = persistence_name
        self.store_id = store_id
        self.base_url = base_url
        self.api_key = api_key
        self.backup_directory = backup_directory
        self.updaters = updaters
