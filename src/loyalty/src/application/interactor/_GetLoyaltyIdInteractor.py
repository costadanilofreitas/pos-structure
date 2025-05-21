from application.model.configuration import Configurations
from application.repository.api import APIRepository
from typing import Optional


class GetLoyaltyIdInteractor(object):
    def __init__(self, configs, api_repository):
        # type: (Configurations, APIRepository) -> None

        self.logger = configs.logger
        self.configs = configs
        self.api_repository = api_repository

    def get_loyalty_id(self, loyalty_customer_id):
        # type: (str) -> Optional[str]

        return self.api_repository.retrieve_loyalty_customer_info(loyalty_customer_id)
