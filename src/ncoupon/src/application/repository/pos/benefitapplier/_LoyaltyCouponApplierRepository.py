import json
from xml.etree import cElementTree as eTree

from application.model import DefaultBenefitApplierRepository, LoyaltyTokens
from application.model.customexception import ErrorBurningCoupon, ErrorUnlockingCoupon
from application.model.customexception._CustomException import ErrorCheckingVoucher
from messagebus import Message, DataType
from msgbus import TK_SYS_ACK, TK_SYS_NAK


class LoyaltyBenefitApplierRepository(DefaultBenefitApplierRepository):
    
    def __init__(self, configs, message_bus):
        super(LoyaltyBenefitApplierRepository, self).__init__(configs, message_bus)
        
        self.benefit = {}

    def check_voucher(self, pos_id, voucher_id):
        # type: (int, str) -> bool

        message = Message(token=LoyaltyTokens.TK_LOYALTY_GET_AND_LOCK_VOUCHER,
                          data=json.dumps(dict(posId=pos_id, voucherId=voucher_id)),
                          data_type=DataType.string)

        response = self.message_bus.send_message("Loyalty", message)
        if response.token == TK_SYS_ACK:
            self.benefit[voucher_id] = response.data
            return True

        if response.data:
            raise ErrorCheckingVoucher(response.data)

        return False
    
    def get_benefit_and_lock(self, voucher_id):
        # type: (str) -> None

        benefit = self.benefit[voucher_id]
        del self.benefit[voucher_id]
        
        return benefit

    def unlock_benefit(self, benefit_id):
        # type: (str) -> None

        message = Message(token=LoyaltyTokens.TK_LOYALTY_UNLOCK_VOUCHER,
                          data=benefit_id,
                          data_type=DataType.string)

        response = self.message_bus.send_message("Loyalty", message)
        if response.token == TK_SYS_NAK:
            raise ErrorUnlockingCoupon(response.data)

    def burn_benefit(self, benefit_id):
        # type: (str) -> None

        message = Message(token=LoyaltyTokens.TK_LOYALTY_BURN_VOUCHER,
                          data=benefit_id,
                          data_type=DataType.string)

        response = self.message_bus.send_message("Loyalty", message)
        if response.token == TK_SYS_NAK:
            raise ErrorBurningCoupon(response.data)
    
    def get_benefit_info(self, data):
        # type: (str) -> None
        
        return

    def get_benefit_id_by_custom_property(self, order_picture):
        # type: (eTree) -> str

        order_properties = order_picture.findall(".//OrderProperty")

        for prop in order_properties:
            key = prop.get("key")

            if key == "LOYALTY_ID":
                return prop.get("value")
