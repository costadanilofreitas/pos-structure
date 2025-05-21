import json

from application.model import DefaultBenefitApplierRepository, BenefitAppliers, OperationDescription, OperationStatus
from application.model.configuration import Configurations
from application.repository.pos import DBRepository
from application.repository.pos.utils import find_benefit_applier
from typing import Dict


class ApplyBenefitInteractor(object):
    
    def __init__(self, configs, db_repository, benefit_appliers_repositories):
        # type: (Configurations, DBRepository, Dict[BenefitAppliers: DefaultBenefitApplierRepository]) -> None
        
        self.configs = configs
        self.logger = self.configs.logger
        self.db_repository = db_repository
        self.benefit_appliers_repositories = benefit_appliers_repositories

    def apply_benefit(self, pos_id, voucher_id):
        # type: (int, str) -> None

        benefit_applier = find_benefit_applier(pos_id, voucher_id)

        self.logger.info("Trying to get and lock benefit to voucherId: {}; PosId: {}; BenefitApplier: {}"
                         .format(voucher_id, pos_id, benefit_applier))

        benefit = self.benefit_appliers_repositories[benefit_applier].get_benefit_and_lock(voucher_id)
        benefit_id = str(json.loads(benefit).get("id"))

        try:
            self.logger.info("Benefit successfully obtained. BenefitId: {}".format(benefit_id))

            self.benefit_appliers_repositories[benefit_applier].add_benefit(pos_id, benefit_id, benefit)

            self.db_repository.insert_or_update_pending_operation(benefit_id,
                                                                  pos_id,
                                                                  OperationDescription.APPLIED,
                                                                  OperationStatus.DONE,
                                                                  benefit_applier,
                                                                  0)
        except Exception as _:
            self.logger.exception("Error applying benefit. BenefitId: {}".format(benefit_id))
            
            self.benefit_appliers_repositories[benefit_applier].unlock_benefit(benefit_id)
            raise
