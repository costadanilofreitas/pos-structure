from xml.etree import cElementTree as eTree

from application.interactor import BurnBenefitInteractor
from application.model import BenefitAppliers, DefaultBenefitApplierRepository
from application.model.configuration import Configurations
from application.repository.pos import DBRepository
from application.repository.pos.utils import find_order_benefits_id, replace_pos_id_by_originator_id
from typing import Dict


class OrderModifiedPaidInteractor(object):
    
    def __init__(self, burn_benefit_interactor, configs, db_repository, benefit_appliers_repositories):
        # type: (BurnBenefitInteractor, Configurations, DBRepository, Dict[BenefitAppliers: DefaultBenefitApplierRepository]) -> None
        
        self.configs = configs
        self.logger = self.configs.logger
        self.db_repository = db_repository
        self.benefit_appliers_repositories = benefit_appliers_repositories
        self.burn_benefit_interactor = burn_benefit_interactor

    def burn_paid_benefit(self, pos_id, order_picture):
        # type: (int, eTree) -> None

        order_benefits_id = find_order_benefits_id(self.logger, order_picture)

        if len(order_benefits_id) > 0:
            self.logger.info("Benefits founded to burn: {}".format(order_benefits_id))
            pos_id = replace_pos_id_by_originator_id(self.logger, pos_id, order_picture)
        
        for benefit_id in order_benefits_id:
            benefit_applier = self.db_repository.get_benefit_applier_by_db(benefit_id, pos_id)
            self.burn_benefit_interactor.burn_benefit(benefit_id, pos_id, benefit_applier)
