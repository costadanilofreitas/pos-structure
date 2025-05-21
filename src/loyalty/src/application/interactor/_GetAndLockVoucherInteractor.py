from typing import Optional

from application.model.configuration import Configurations
from application.repository.api import APIRepository


class GetAndLockVoucherInteractor(object):
    def __init__(self, configs, api_repository):
        # type: (Configurations, APIRepository) -> None

        self.logger = configs.logger
        self.configs = configs
        self.api_repository = api_repository

    def get_and_lock_voucher(self, pos_id, voucher_id):
        # type: (int, str) -> Optional[str]

        return self.api_repository.retrieve_benefit(pos_id, voucher_id)
