from logging import Logger

from typing import List


class Configurations(object):
    def __init__(self,
                 required_services=None,
                 service_name=None,
                 persistence_name=None,
                 logger=None,
                 supported_benefit_appliers=None,
                 retry_frequency=None,
                 max_retry_number=None,
                 retry_min_time_to_try_again=None):
        # type: (str, str, str, Logger, List[str], int, int, int) -> None

        self.required_services = required_services
        self.service_name = service_name
        self.persistence_name = persistence_name
        self.logger = logger
        self.supported_benefit_appliers = supported_benefit_appliers
        self.retry_frequency = retry_frequency
        self.max_retry_quantity = max_retry_number
        self.retry_min_time_to_try_again = retry_min_time_to_try_again
