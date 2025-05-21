import time
from json import dumps
from logging import Logger
from xml.etree import cElementTree as eTree

from application.model import ProductNotFound
from application.model.benefit import Benefit
from application.model.order import Order
from application.repository import NDiscountRepository
from posot import OrderTakerException
from sysactions import get_model, get_posot, get_pricelist


class AddBenefitToApplyUnitOfWork:
    def __init__(self, logger, pos_id, benefit, raw_benefit):
        # type: (Logger, int, Benefit, dict) -> None

        self.logger = logger
        self.pos_id = pos_id
        self.benefit = benefit
        self.raw_benefit = raw_benefit
        self.order = NDiscountRepository.get_order(
            self.pos_id,
            create_order=any([a.name == "itemsToAdd" for a in self.benefit.actions])
        )
        self.model = get_model(pos_id)
        self.pos_ot = get_posot(self.model)
        self.added_sale_lines = []
        self.promotion_tenders = 0
        items_to_burn = Order.get_items_to_burn(self.order, self.benefit) if self.benefit.conditions.burn_items else {}
        self.items_to_burn = items_to_burn

    def _get_updated_order(self):
        self.model = get_model(self.pos_id)
        self.pos_ot = get_posot(self.model)
        return NDiscountRepository.get_order(
            self.pos_id,
            create_order=any([a.name == "itemsToAdd" for a in self.benefit.actions])
        )

    def update_order(self):
        self.order = NDiscountRepository.get_order(
            self.pos_id,
            create_order=any([a.name == "itemsToAdd" for a in self.benefit.actions])
        )

    def add_sale_line(self, item_id, quantity, is_free=False, price=None):
        # type: (int, int, bool, float) -> None

        if int(item_id) not in NDiscountRepository.get_all_products():
            raise ProductNotFound()

        free = False if price is not None else is_free
        n_sale_lines = len(self.order.sale_lines)

        context_id = "1.%s" % item_id
        added_sale_line = eTree.XML(self.pos_ot.doSale(self.pos_id,
                                                       context_id,
                                                       pricelist=get_pricelist(self.model),
                                                       qtty=quantity))

        added_sale_line_number = int(added_sale_line.get("lineNumber"))

        self.logger.info("New sale line added. LineNumber: {}; ItemId: {}".format(added_sale_line_number, context_id))

        self.added_sale_lines.append(added_sale_line_number)
        tender_amount = 0

        updated_order = self._get_updated_order()
        time_limit = time.time() + 5.0
        while time.time() < time_limit and len(updated_order.sale_lines) == n_sale_lines:
            updated_order = self._get_updated_order()
            time.sleep(0.1)

        if price is not None:
            self.pos_ot.priceOverwrite(self.pos_id, added_sale_line_number, str(price))
            self.logger.info("Price overwritten. New Price: {}".format(str(price)))

        for sale_line in updated_order.sale_lines:
            if int(sale_line.line_number) == int(added_sale_line_number):
                if free:
                    tender_amount += sale_line.item_price
                self.items_to_burn[sale_line.key] = sale_line.qty + int(self.items_to_burn.get(sale_line.key, 0))

        self.promotion_tenders += tender_amount

    def save(self):
        NDiscountRepository.add_benefit_to_apply(dumps(self.raw_benefit),
                                                 self.model,
                                                 self.pos_ot,
                                                 self.items_to_burn,
                                                 self.added_sale_lines,
                                                 self.promotion_tenders)

    def rollback(self):
        try:
            self.logger.error("Rollback changes...")
            valid_sale_lines = [sl for sl in self._get_updated_order().sale_lines if sl.level == 0 and sl.qty > 0]
            valid_sale_lines_qty = len(valid_sale_lines)
            if valid_sale_lines_qty == self.added_sale_lines:
                self.pos_ot.voidOrder(self.pos_id)
                return
            self.pos_ot.voidLine(self.pos_id, "|".join([str(sl) for sl in self.added_sale_lines]))
        except OrderTakerException:
            pass
