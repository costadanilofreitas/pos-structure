from xml.etree import cElementTree as eTree

from application.model import DefaultBenefitApplierRepository, BenefitAppliers
from application.model.configuration import Configurations
from application.repository.pos import DBRepository
from application.repository.pos.utils import find_order_benefits_id, replace_pos_id_by_originator_id
from typing import Dict


class OrderModifiedTotalInteractor(object):
    
    def __init__(self, configs, db_repository, benefit_appliers_repositories):
        # type: (Configurations, DBRepository, Dict[BenefitAppliers: DefaultBenefitApplierRepository]) -> None
        
        self.configs = configs
        self.logger = self.configs.logger
        self.db_repository = db_repository
        self.benefit_appliers_repositories = benefit_appliers_repositories

    def apply_benefit_tenders(self, pos_id, order_id, order_picture):
        # type: (str, str, eTree) -> None

        order_benefits_id = find_order_benefits_id(self.logger, order_picture)
        
        if len(order_benefits_id) > 0:
            self.logger.info("Benefits founded to apply: {}".format(order_benefits_id))
            pos_id = replace_pos_id_by_originator_id(self.logger, pos_id, order_picture)
        
        if order_benefits_id:
            self.logger.info("Removing not used benefits for posId: {}; orderId: {}".format(pos_id, order_id))
            self.benefit_appliers_repositories[BenefitAppliers.N_DISCOUNT].verify_and_remove_benefits(pos_id)
            self.logger.info("Applying promotional tenders for posId: {}; orderId: {}".format(pos_id, order_id))
            self.benefit_appliers_repositories[BenefitAppliers.N_DISCOUNT].apply_promotion_tenders(pos_id)
