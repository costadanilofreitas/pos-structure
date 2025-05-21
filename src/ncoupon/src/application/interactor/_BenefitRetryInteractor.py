from application.interactor import BurnBenefitInteractor, UnlockBenefitInteractor
from application.model import BenefitControllerDto, OperationDescription
from application.model.configuration import Configurations
from application.repository.pos import DBRepository
from typing import List, Optional


class BenefitRetryInteractor(object):
    
    def __init__(self, configs, db_repository, burn_benefit_interactor, unlock_benefit_interactor):
        # type: (Configurations, DBRepository, BurnBenefitInteractor, UnlockBenefitInteractor) -> None

        self.configs = configs
        self.logger = self.configs.logger
        self.db_repository = db_repository
        self.burn_interactor = burn_benefit_interactor
        self.unlock_interactor = unlock_benefit_interactor

    def get_pending_operations_benefits(self):
        # type: () -> Optional[List[BenefitControllerDto]]
        
        return self.db_repository.find_pending_operations()

    def perform_operations_on_pending_benefits(self, pending_operations):
        # type: (List[BenefitControllerDto]) -> None
        
        for benefit in pending_operations:
            default_params = [benefit.benefit_id, benefit.pos_id, benefit.benefit_applier, benefit.retry_quantity]
            
            if benefit.operation_description == OperationDescription.BURNED:
                self.burn_interactor.burn_benefit(*default_params)
            elif benefit.operation_description == OperationDescription.UNLOCKED:
                self.unlock_interactor.unlock_benefit(*default_params)
