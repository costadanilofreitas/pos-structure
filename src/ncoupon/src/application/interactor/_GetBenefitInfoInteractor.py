from application.model import BenefitAppliers, DefaultBenefitApplierRepository
from application.model.configuration import Configurations
from application.model.customexception import ErrorObtainingCouponInfo
from application.repository.pos import DBRepository
from application.repository.pos.utils import find_benefit_applier
from msgbus import TK_SYS_NAK
from typing import Dict


class GetBenefitInfoInteractor(object):
    
    def __init__(self, configs, db_repository, benefit_appliers_repositories):
        # type: (Configurations, DBRepository, Dict[BenefitAppliers: DefaultBenefitApplierRepository]) -> None
        
        self.configs = configs
        self.logger = self.configs.logger
        self.db_repository = db_repository
        self.benefit_appliers_repositories = benefit_appliers_repositories

    def get_benefit_info(self, pos_id, voucher_id):
        # type: (int, str) -> str

        benefit_applier = find_benefit_applier(pos_id, voucher_id)

        response = self.benefit_appliers_repositories[benefit_applier].get_benefit_info(voucher_id)
        if response.token == TK_SYS_NAK:
            raise ErrorObtainingCouponInfo(response.data)

        return response.data
