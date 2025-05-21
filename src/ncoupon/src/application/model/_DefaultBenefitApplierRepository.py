import json
from abc import abstractmethod
from xml.etree import cElementTree as eTree

from application.model import NDiscountTokens
from application.model.configuration import Configurations
from application.model.customexception import ErrorApplyingBenefit
from mbcontextmessagehandler import MbContextMessageBus
from messagebus import Message, DataType
from msgbus import TK_SYS_NAK
from typing import Optional


class DefaultBenefitApplierRepository(object):
    
    def __init__(self, configs, message_bus):
        # type: (Configurations, MbContextMessageBus) -> None

        self.logger = configs.logger
        self.configs = configs
        self.message_bus = message_bus

    def add_benefit(self, pos_id, benefit_id, benefit):
        # type: (int, str, str) -> None

        data = json.dumps(dict(posId=pos_id, benefitId=benefit_id, benefit=json.loads(benefit)))

        message = Message(token=NDiscountTokens.TK_NDISCOUNT_ADD_BENEFIT,
                          data=data,
                          data_type=DataType.string)

        response = self.message_bus.send_message("nDiscount", message)
        if response.token == TK_SYS_NAK:
            raise ErrorApplyingBenefit(response.data)
    
    def remove_benefit(self, pos_id, benefit_ids=None):
        # type: (int, Optional[str, list, None]) -> Message
        
        data = json.dumps(dict(pos_id=pos_id, benefit=benefit_ids))
        message = Message(token=NDiscountTokens.TK_NDISCOUNT_REMOVE,
                          data=data,
                          data_type=DataType.string)
    
        return self.message_bus.send_message("nDiscount", message)

    def verify_and_remove_benefits(self, pos_id):
        # type: (str) -> Message
    
        message = Message(token=NDiscountTokens.TK_NDISCOUNT_VERIFY_AND_REMOVE,
                          data=json.dumps({"pos_id": pos_id}),
                          data_type=DataType.string)
    
        return self.message_bus.send_message("nDiscount", message)

    def apply_promotion_tenders(self, pos_id):
        # type: (int) -> Message
    
        message = Message(token=NDiscountTokens.TK_NDISCOUNT_APPLY_PROMOTION_TENDERS,
                          data=json.dumps({"pos_id": int(pos_id)}),
                          data_type=DataType.string)
    
        return self.message_bus.send_message("nDiscount", message)

    @abstractmethod
    def check_voucher(self, pos_id, benefit_id):
        # type: (int, str) -> None
        
        raise NotImplementedError()

    @abstractmethod
    def get_benefit_and_lock(self, benefit_id):
        # type: (str) -> str

        raise NotImplementedError()

    @abstractmethod
    def unlock_benefit(self, benefit_id):
        # type: (str) -> None

        raise NotImplementedError()

    @abstractmethod
    def burn_benefit(self, benefit_id):
        # type: (str) -> None

        raise NotImplementedError()

    @abstractmethod
    def get_benefit_info(self, data):
        # type: (str) -> None
        
        raise NotImplementedError()

    @abstractmethod
    def get_benefit_id_by_custom_property(self, order_picture):
        # type: (eTree) -> str

        raise NotImplementedError()
