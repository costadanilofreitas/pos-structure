from application.model.configuration import Configurations
from application.repository.api import APIRepository


class UnlockVoucherInteractor(object):
    def __init__(self, configs, api_repository):
        # type: (Configurations, APIRepository) -> None

        self.logger = configs.logger
        self.configs = configs
        self.api_repository = api_repository

    def unlock_benefit(self, benefit_id):
        # type: (str) -> None

        self.api_repository.unlock_benefit(benefit_id)
