from xml.etree import cElementTree as eTree

from application.interactor import UnlockBenefitInteractor
from application.model import DefaultBenefitApplierRepository, BenefitAppliers
from application.model.configuration import Configurations
from application.repository.pos import DBRepository
from application.repository.pos.utils import find_order_benefits_id, replace_pos_id_by_originator_id
from typing import Dict


class OrderModifiedVoidLineInteractor(object):
    
    def __init__(self, unlock_benefit_interactor, configs, db_repository, benefit_appliers_repositories):
        # type: (UnlockBenefitInteractor, Configurations, DBRepository, Dict[BenefitAppliers: DefaultBenefitApplierRepository]) -> None
        
        self.configs = configs
        self.logger = self.configs.logger
        self.db_repository = db_repository
        self.benefit_appliers_repositories = benefit_appliers_repositories
        self.unlock_benefit_interactor = unlock_benefit_interactor

    def remove_benefits(self, pos_id, order_picture):
        # type: (str, eTree) -> None

        order_benefits_id = find_order_benefits_id(self.logger, order_picture, validate_voided_lines=True)

        if len(order_benefits_id) > 0:
            self.logger.info("Benefits founded to unlock: {}".format(order_benefits_id))
            pos_id = replace_pos_id_by_originator_id(self.logger, pos_id, order_picture)
        
        for benefit_id in order_benefits_id:
            benefit_applier = self.db_repository.get_benefit_applier_by_db(benefit_id, pos_id)
            self.unlock_benefit_interactor.unlock_benefit(benefit_id, pos_id, benefit_applier)

        if order_benefits_id:
            order_id = order_picture.get("orderId")
            self.logger.info("Removing not used benefits for posId: {}; orderId: {}".format(pos_id, order_id))
            self.benefit_appliers_repositories[BenefitAppliers.N_DISCOUNT].verify_and_remove_benefits(pos_id)
