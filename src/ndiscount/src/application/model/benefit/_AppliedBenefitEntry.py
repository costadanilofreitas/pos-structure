from json import loads, dumps

from . import Benefit


class AppliedBenefitEntry(object):
    def __init__(self, benefit_obj, used_discount_ids, added_sale_lines, burnt_items, promotion_tender_amount):
        # type: (dict, list[int], list[int], dict, float) -> None

        self.benefit = Benefit.from_self_stored_json(benefit_obj)
        self.used_discount_ids = used_discount_ids
        self.added_sale_lines = added_sale_lines
        self.burnt_items = burnt_items
        self.promotion_tender_amount = promotion_tender_amount

    def to_json(self):
        # type: () -> dict
        return dumps({
                "benefit": loads(self.benefit.to_json()),
                "used_discount_ids": list(self.used_discount_ids),
                "added_sale_lines": list(self.added_sale_lines),
                "burnt_items": self.burnt_items if self.benefit.conditions.burn_items else dict(),
                "promotion_tender_amount": self.promotion_tender_amount
        })
