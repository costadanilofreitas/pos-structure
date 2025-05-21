from application.model import DefaultBenefitApplierRepository, BenefitAppliers, OperationDescription
from application.model.configuration import Configurations
from application.repository.pos import DBRepository
from typing import Optional, Dict


class BurnBenefitInteractor(object):
    
    def __init__(self, configs, db_repository, benefit_appliers_repositories):
        # type: (Configurations, DBRepository, Dict[BenefitAppliers: DefaultBenefitApplierRepository]) -> None

        self.configs = configs
        self.logger = self.configs.logger
        self.db_repository = db_repository
        self.benefit_appliers_repositories = benefit_appliers_repositories

    def burn_benefit(self, benefit_id, pos_id, benefit_applier, retry_quantity=0):
        # type: (str, int, BenefitAppliers, Optional[int]) -> None
        
        success = False
        try:
            self.logger.info("Burning benefit. BenefitId: {}; PosId: {}; BenefitApplier: {}; RetryQuantity: {}"
                             .format(benefit_id, pos_id, benefit_applier, retry_quantity))
            self.benefit_appliers_repositories[benefit_applier].burn_benefit(benefit_id)
            success = True
        except Exception as _:
            self.logger.exception("Error burning benefit: {}".format(benefit_id))
        finally:
            self.db_repository.manage_operation_status(success,
                                                       benefit_id,
                                                       pos_id,
                                                       OperationDescription.BURNED,
                                                       benefit_applier,
                                                       retry_quantity)
