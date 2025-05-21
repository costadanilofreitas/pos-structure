from application.model import OperationDescription, BenefitAppliers, DefaultBenefitApplierRepository
from application.model.configuration import Configurations
from application.repository.pos import DBRepository
from typing import Optional, Dict


class UnlockBenefitInteractor(object):
    
    def __init__(self, configs, db_repository, benefit_appliers_repositories):
        # type: (Configurations, DBRepository, Dict[BenefitAppliers: DefaultBenefitApplierRepository]) -> None

        self.configs = configs
        self.logger = self.configs.logger
        self.db_repository = db_repository
        self.benefit_appliers_repositories = benefit_appliers_repositories

    def unlock_benefit(self, benefit_id, pos_id, benefit_applier, retry_quantity=0):
        # type: (str, int, BenefitAppliers, Optional[int]) -> None

        self.logger.info("Trying to unlock the benefit: {}".format(benefit_id))

        success = False
        try:
            self.logger.info("Unlocking benefit. BenefitId: {}; PosId: {}; BenefitApplier: {}; RetryQuantity: {}"
                             .format(benefit_id, pos_id, benefit_applier, retry_quantity))

            self.benefit_appliers_repositories[benefit_applier].unlock_benefit(benefit_id)
            success = True
        except Exception as _:
            self.logger.exception("Error unlocking benefit: {}".format(benefit_id))
        finally:
            self.db_repository.manage_operation_status(success,
                                                       benefit_id,
                                                       pos_id,
                                                       OperationDescription.BURNED,
                                                       benefit_applier,
                                                       retry_quantity)
