from application.model import Configurations, BenefitNotFound
from application.model.benefit import ActionTypes
from application.model.transactions import AddBenefitToApplyUnitOfWork
from application.repository import NDiscountRepository
from application.validator import BenefitValidator


class AddBenefitToApplyInteractor:

    def __init__(self, configs, repository):
        # type: (Configurations, NDiscountRepository) -> None
        self.configs = configs
        self.logger = configs.logger
        self.repository = repository

    def get_benefit_from_database(self, benefit_id):
        # type: (str) -> str

        benefit = self.repository.get_benefit_from_database(benefit_id)
        if not benefit:
            raise BenefitNotFound("NDISCOUNT_BENEFIT_NOT_FOUND")

        return benefit

    def apply(self, uow):
        # type: (AddBenefitToApplyUnitOfWork) -> None

        BenefitValidator.validate_benefit_for_model(uow.benefit, uow.model)

        benefits_to_apply = NDiscountRepository.get_benefits_to_apply(uow.model)

        burnt_items = {}
        for benefit_to_apply in benefits_to_apply:
            burnt_items.update(benefit_to_apply.get("burnt_items"))

        BenefitValidator.validate_benefit_for_order(uow.benefit, uow.order, benefits_to_apply, burnt_items)

        for action in uow.benefit.actions:
            if action.name == ActionTypes.itemsToAdd.value:
                for entry in action.value:
                    item_id = entry.get("item")
                    quantity = entry.get("quantity")
                    free = bool(entry.get("free"))
                    price = entry.get("price", None)

                    uow.add_sale_line(item_id, quantity, free, price)

        uow.save()
