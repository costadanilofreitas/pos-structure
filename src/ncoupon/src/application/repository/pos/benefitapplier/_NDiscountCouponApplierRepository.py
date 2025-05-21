import json
from xml.etree import cElementTree as eTree

from application.model import DefaultBenefitApplierRepository, NDiscountTokens
from messagebus import Message, DataType
from msgbus import TK_SYS_ACK


class NDiscountCouponApplierRepository(DefaultBenefitApplierRepository):
    
    def __init__(self, configs, message_bus):
        super(NDiscountCouponApplierRepository, self).__init__(configs, message_bus)
        
        self.benefit = {}

    def check_voucher(self, pos_id, benefit_id):
        # type: (int, str) -> bool

        message = Message(token=NDiscountTokens.TK_NDISCOUNT_CHECK_STORED_BENEFIT,
                          data=json.dumps(dict(benefitId=benefit_id)),
                          data_type=DataType.string)

        response = self.message_bus.send_message("nDiscount", message)
        if response.token == TK_SYS_ACK:
            self.benefit[benefit_id] = response.data
            return True
        return False
    
    def get_benefit_and_lock(self, benefit_id):
        # type: (str) -> None

        benefit = self.benefit[benefit_id]
        del self.benefit[benefit_id]
        
        return benefit

    def unlock_benefit(self, benefit_id):
        # type: (str) -> None

        return

    def burn_benefit(self, benefit_id):
        # type: (str) -> None

        return
    
    def get_benefit_info(self, data):
        # type: (str) -> None
        
        return

    def get_benefit_id_by_custom_property(self, order_picture):
        # type: (eTree) -> None

        return
