from logging import Logger


class Configurations(object):
    def __init__(self, required_services=None, service_name=None, persistence_name=None, logger=None,
                 promotional_tender_type_id=None):
        # type: (str, str, str, Logger, str) -> None

        self.service_name = service_name
        self.required_services = required_services
        self.persistence_name = persistence_name
        self.logger = logger
        self.promotional_tender_type_id = promotional_tender_type_id
