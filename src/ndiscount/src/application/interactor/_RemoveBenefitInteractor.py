from xml.etree import cElementTree as eTree

from posot import OrderTaker
from application.model import Configurations
from application.repository import NDiscountRepository


class RemoveBenefitInteractor(object):

    def __init__(self, configs, repository):
        # type: (Configurations, NDiscountRepository) -> None

        self.configs = configs
        self.repository = repository

    @staticmethod
    def remove_all_benefits(model, pos_ot):
        # type: (eTree, OrderTaker) -> None

        benefits_to_apply = NDiscountRepository.get_benefits_to_apply(model)
        added_sale_lines = set()
        used_discount_ids = set()

        for benefit_to_apply in benefits_to_apply:
            added_sale_lines.update(benefit_to_apply.get("added_sale_lines", []))
            used_discount_ids.update(benefit_to_apply.get("used_discount_ids", []))

        for discount_id in used_discount_ids:
            pos_ot.clearDiscount(discount_id)

    @staticmethod
    def remove_benefit_by_id(pos_id, model, pos_ot, benefit_id):
        # type: (int, eTree, OrderTaker, str) -> None

        benefits_to_apply = NDiscountRepository.get_benefits_to_apply_by_id(model, benefit_id)
        added_sale_lines = set()
        used_discount_ids = set()

        for benefit_to_apply in benefits_to_apply:
            added_sale_lines.update(benefit_to_apply.get("added_sale_lines", []))
            used_discount_ids.update(benefit_to_apply.get("used_discount_ids", []))

        if len(added_sale_lines) > 0:
            lines_to_void = "|".join([str(x) for x in added_sale_lines])
            pos_ot.voidLine(pos_id, lines_to_void)

        for discount_id in used_discount_ids:
            pos_ot.clearDiscount(discount_id)

        NDiscountRepository.delete_benefit_to_apply(benefit_id, pos_ot, model)
