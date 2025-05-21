from logging import Logger


class Configurations(object):
    def __init__(self,
                 required_services=None,
                 service_name=None,
                 persistence_name=None,
                 store_id=None,
                 logger=None,
                 base_url=None,
                 api_key=None):
        # type: (str, str, str, int, Logger, str, str) -> None

        self.required_services = required_services
        self.service_name = service_name
        self.persistence_name = persistence_name
        self.store_id = store_id
        self.logger = logger
        self.base_url = base_url
        self.api_key = api_key
        self.endpoints = Endpoints()
        
        
class Endpoints(object):
    def __init__(self):
        self.retrieve_loyalty_id = None
        self.retrieve_benefit = None
        self.burn_benefit = None
        self.unlock_benefit = None
