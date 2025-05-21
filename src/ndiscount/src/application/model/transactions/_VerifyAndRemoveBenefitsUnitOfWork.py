from sysactions import get_model, get_posot
from application.repository import NDiscountRepository


class VerifyAndRemoveBenefitsUnitOfWork:
    def __init__(self, pos_id):
        # type: (int) -> None
        self.pos_id = pos_id
        self.model = get_model(self.pos_id)
        self.pos_ot = get_posot(self.model)
        self.order = NDiscountRepository.get_order(self.pos_id)
