from application.model import Configurations
from application.model.order import Order
from application.repository import NDiscountRepository
from posot import OrderTaker


class ApplyBenefitsInteractor:

    def __init__(self, configs, repository):
        # type: (Configurations, NDiscountRepository) -> None
        self.configs = configs
        self.logger = configs.logger
        self.repository = repository

    @staticmethod
    def get_burnt_items(burnt_items_list):
        burnt_items = {}
        for burnt_item_dict in burnt_items_list:
            for key, value in burnt_item_dict.items():
                burnt_items[key] = burnt_items.get(key, 0) + value
        return burnt_items

    def apply(self, pos_id, pos_ot, order, benefits_to_apply):
        # type: (int, OrderTaker, Order, list[dict]) -> None

        benefits_to_apply = sorted(benefits_to_apply, key=lambda k: k.get("benefit").priority)
        burnt_items = ApplyBenefitsInteractor.get_burnt_items([x.get("burnt_items") for x in benefits_to_apply])
        promotion_tender_amount = sum([x.get("promotion_tender_amount", 0) for x in benefits_to_apply])
        order.total_amount = order.total_amount - promotion_tender_amount
        available_discount_ids = Order.get_available_discount_ids(pos_ot)
        used_discount_ids = set()
        next_benefits_to_apply = []

        for benefit_to_apply in benefits_to_apply:
            benefit = benefit_to_apply.get("benefit")
            benefit_used_discount_ids = set()
            benefit_burnt_items = {}

            for action in benefit.actions:
                action_used_discount_ids, action_burnt_items = NDiscountRepository.execute_action(
                        action, order, pos_ot, available_discount_ids)
                benefit_used_discount_ids.update(action_used_discount_ids)
                benefit_burnt_items = ApplyBenefitsInteractor.get_burnt_items(
                    [action_burnt_items, benefit_burnt_items])

            burnt_items = ApplyBenefitsInteractor.get_burnt_items([burnt_items, benefit_burnt_items])
            used_discount_ids.update(benefit_used_discount_ids)
            next_benefits_to_apply.append({
                "benefit": benefit_to_apply.get("raw_benefit"),
                "promotion_tender_amount": benefit_to_apply.get("promotion_tender_amount", 0),
                "burnt_items": benefit_to_apply.get("burnt_items", {}),
                "added_sale_lines": benefit_to_apply.get("added_sale_lines", []),
                "used_discount_ids": list(benefit_used_discount_ids)
            })

        NDiscountRepository.set_benefits_to_apply(next_benefits_to_apply, pos_ot)
        if promotion_tender_amount > 0:
            self.logger.info("Applying promotional tender. Promotion tender amount: {}".format(promotion_tender_amount))
            self.repository.apply_promotional_tender_amount(pos_id, promotion_tender_amount)
