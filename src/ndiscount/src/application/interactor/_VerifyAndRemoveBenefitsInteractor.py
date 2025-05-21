from json import loads

from application.interactor import RemoveBenefitInteractor
from application.model import Configurations, OrderValidationException
from application.model.benefit import Benefit
from application.model.transactions import VerifyAndRemoveBenefitsUnitOfWork
from application.repository import NDiscountRepository
from application.validator import BenefitValidator


class VerifyAndRemoveBenefitsInteractor(object):

    def __init__(self, configs, remove_benefit_interactor, repository):
        # type: (Configurations, RemoveBenefitInteractor, NDiscountRepository) -> None

        self.configs = configs
        self.remove_benefit_interactor = remove_benefit_interactor
        self.repository = repository

    @staticmethod
    def merge_counting_dicts(burnt_items_list):
        # type: (list[dict]) -> dict
        """Merge burnt items from benefits"""

        burnt_items = {}
        for d in burnt_items_list:
            for key, value in d.items():
                burnt_items[key] = value + burnt_items.get(key, 0)

        return burnt_items

    @staticmethod
    def unmerge_counting_dict(subtract_from, items_not_to_burn):
        # type: (dict, dict) -> dict
        """Unburn items to verify benefit"""

        burnt_items = subtract_from.copy()
        for key, value in items_not_to_burn.items():
            burnt_items[key] = burnt_items.get(key, 0) - value

        return burnt_items

    def verify_and_remove(self, uow):
        # type: (VerifyAndRemoveBenefitsUnitOfWork) -> None

        benefits_to_apply = NDiscountRepository.get_benefits_to_apply(uow.model)

        burnt_items = VerifyAndRemoveBenefitsInteractor.merge_counting_dicts([
            benefit_to_apply.get("burnt_items", {}) for benefit_to_apply in benefits_to_apply
        ])
        n_voided_sale_lines = 0
        n_sale_lines = len(set([s.line_number for s in uow.order.sale_lines if int(s.level) == 0 and int(s.qty) > 0]))

        for benefit_to_apply in benefits_to_apply:
            benefit = Benefit.from_benefit_json(loads(benefit_to_apply.get("benefit")))
            burnt_items_for_benefit = VerifyAndRemoveBenefitsInteractor.unmerge_counting_dict(burnt_items,
                                                                                              benefit_to_apply.get(
                                                                                                  "burnt_items", {}))
            added_sale_lines = set(benefit_to_apply.get("added_sale_lines", []))

            try:
                BenefitValidator.validate_benefit_for_order(benefit, uow.order, benefits_to_apply,
                                                            burnt_items_for_benefit)
                added_sale_lines_copy = added_sale_lines.copy()
                for sale_line in uow.order.sale_lines:
                    n = int(sale_line.line_number)
                    if n in added_sale_lines_copy and int(sale_line.level) == 0 and int(sale_line.qty) > 0:
                        added_sale_lines_copy.remove(int(sale_line.line_number))
                if len(added_sale_lines_copy) > 0:
                    raise OrderValidationException()

            except OrderValidationException:
                NDiscountRepository.delete_benefit_to_apply(benefit.id, uow.pos_ot, uow.model)
                if len(added_sale_lines) > 0:
                    uow.pos_ot.voidLine(uow.pos_id, "|".join([str(x) for x in added_sale_lines]))

        if len(benefits_to_apply) > 0 and (n_sale_lines == 0 or n_sale_lines == n_voided_sale_lines):
            uow.pos_ot.voidOrder(uow.pos_id)
