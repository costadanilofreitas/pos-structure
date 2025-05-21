from application.model.configuration import Configurations
from application.repository.api import APIRepository


class BurnVoucherInteractor(object):
    def __init__(self, configs, api_repository):
        # type: (Configurations, APIRepository) -> None

        self.logger = configs.logger
        self.configs = configs
        self.api_repository = api_repository

    def burn_benefit(self, benefit_id):
        # type: (str) -> None

        self.api_repository.burn_benefit(benefit_id)
