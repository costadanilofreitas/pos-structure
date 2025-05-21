from application.model import Configurations
from application.repository import NDiscountRepository


class CheckStoredBenefitInteractor(object):

    def __init__(self, configs, repository):
        # type: (Configurations, NDiscountRepository) -> None

        self.configs = configs
        self.repository = repository

    def check_stored_benefit(self, benefit_id):
        # type: (str) -> bool

        return self.repository.get_benefit_from_database(benefit_id)
