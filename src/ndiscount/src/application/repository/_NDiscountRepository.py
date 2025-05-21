import json
from json import loads, dumps
from threading import Lock
from xml.etree import cElementTree as eTree

import sysactions
from application.model import Configurations, OrderNotFoundException
from application.model.benefit import Action, ActionTypes, AppliedBenefitEntry
from application.model.order import Order
from application.util import wait
from mbcontextmessagehandler import MbContextMessageBus
from mwhelper import BaseRepository
from persistence import Connection
from posot import OrderTaker, OrderTakerException
from sysactions import get_current_order
from typing import Optional, List

PRODUCT_ITEMS_CACHE = []
NDISCOUNT_WAIT_SCREEN_DLG_ID = {}


class NDiscountRepository(BaseRepository):

    def __init__(self, configs, message_bus):
        # type: (Configurations, MbContextMessageBus) -> None
        super(NDiscountRepository, self).__init__(message_bus.mbcontext)

        self.logger = configs.logger
        self.configs = configs
        self.message_bus = message_bus
        self.popup_lock = Lock()

    def show_wait_screen(self, pos_id):
        global NDISCOUNT_WAIT_SCREEN_DLG_ID

        self.logger.info("[SHOW] Starting - Dialog manager: {}".format(NDISCOUNT_WAIT_SCREEN_DLG_ID))

        with self.popup_lock:
            if pos_id in NDISCOUNT_WAIT_SCREEN_DLG_ID:
                NDISCOUNT_WAIT_SCREEN_DLG_ID[pos_id]["count"] += 1
            else:
                dlg_id = sysactions.show_messagebox(pos_id,
                                                    message="$NDISCOUNT_VERIFYING_BENEFIT_PLEASE_WAIT",
                                                    title="$LOYALTY_SERVICE",
                                                    buttons="",
                                                    asynch=True,
                                                    timeout=90000000)
                NDISCOUNT_WAIT_SCREEN_DLG_ID[pos_id] = {"dlg_id": dlg_id, "count": 1}

        self.logger.info("[SHOW] Ending - Dialog manager: {}".format(NDISCOUNT_WAIT_SCREEN_DLG_ID))

    def hide_wait_screen(self, pos_id):
        global NDISCOUNT_WAIT_SCREEN_DLG_ID

        self.logger.info("[HIDE] Starting - Dialog manager: {}".format(NDISCOUNT_WAIT_SCREEN_DLG_ID))

        with self.popup_lock:
            if pos_id in NDISCOUNT_WAIT_SCREEN_DLG_ID:

                if NDISCOUNT_WAIT_SCREEN_DLG_ID[pos_id]["count"] == 1:
                    sysactions.close_asynch_dialog(pos_id, NDISCOUNT_WAIT_SCREEN_DLG_ID[pos_id]["dlg_id"])
                    del NDISCOUNT_WAIT_SCREEN_DLG_ID[pos_id]
                else:
                    NDISCOUNT_WAIT_SCREEN_DLG_ID[pos_id]["count"] -= 1

        self.logger.info("[HIDE] Ending - Dialog manager: {}".format(NDISCOUNT_WAIT_SCREEN_DLG_ID))

    def apply_promotional_tender_amount(self, pos_id, amount):
        # type: (int, float) -> None

        model = sysactions.get_model(pos_id)
        pos_ot = sysactions.get_posot(model)
        order_picture = sysactions.get_current_order(model)
        due_amount = float(order_picture.get("dueAmount"))
        tender_amount = str(min(amount, due_amount))
        tender_detail = json.dumps(dict(promotionalTender=True))

        pos_ot.doTender(pos_id,
                        self.configs.promotional_tender_type_id,
                        tender_amount,
                        donotclose=True,
                        tenderdetail=tender_detail)

        self.logger.info("Applied tender amount: {}".format(tender_amount))

    def get_benefit_from_database(self, benefit_id):
        # type: (str) -> Optional[str]

        def inner_func(conn):
            # type: (Connection) -> Optional[str]

            query = "SELECT BenefitJSON FROM StoredBenefits WHERE BenefitId = '{}'".format(benefit_id)
            cursor = conn.select(query)
            if not cursor.rows():
                return

            return cursor.get_row(0).get_entry(0)

        return self.execute_with_connection(inner_func, service_name=self.configs.persistence_name)

    def get_all_products_from_database(self):
        # type: () -> None

        global PRODUCT_ITEMS_CACHE

        def inner_func(conn):
            # type: (Connection) -> List[int]

            query = "SELECT ProductCode FROM Product"
            cursor = conn.select(query)

            all_products = []
            for row in cursor:
                product_item = int(row.get_entry(0))
                all_products.append(product_item)

            return all_products

        PRODUCT_ITEMS_CACHE = self.execute_with_connection(inner_func, service_name="Persistence")

    @staticmethod
    def get_all_products():
        # type: () -> List[int]

        return PRODUCT_ITEMS_CACHE

    @staticmethod
    def get_order_xml(pos_id, model=None):
        # type: (int, Optional[eTree]) -> eTree

        if not model:
            model = sysactions.get_model(pos_id)
        return sysactions.get_current_order(model)

    @staticmethod
    def get_order_state_from_pos_id(order_xml):
        # type: (eTree) -> str

        if order_xml is None:
            return "UNDEFINED"

        state_history = order_xml.findall(".//State") if order_xml else []
        state = state_history[-1].get("state", "UNDEFINED") if len(state_history) > 0 else "UNDEFINED"

        return state.upper()

    @staticmethod
    def get_order(pos_id, create_order=False):
        # type: (int, bool) -> Order

        model = sysactions.get_model(pos_id)
        pos_ot = sysactions.get_posot(model)
        order_xml = NDiscountRepository.get_order_xml(pos_id, model)

        state = NDiscountRepository.get_order_state_from_pos_id(order_xml)
        if state not in ["IN_PROGRESS", "TOTALED", "RECALLED"]:
            if not create_order:
                raise OrderNotFoundException()

            pos_ot.createOrder(model.get("posId"), sysactions.get_pricelist(model), saletype="EAT_IN")
            for _ in wait(5):
                model = sysactions.get_model(pos_id)
                order_xml = NDiscountRepository.get_order_xml(pos_id, model)
                if NDiscountRepository.get_order_state_from_pos_id(order_xml) == "IN_PROGRESS":
                    break
            if order_xml is None:
                raise OrderNotFoundException()

        session = [v for v in order_xml.get("sessionId", "").split(",") if v.startswith("user=")]
        user_id = session[0].replace("user=", "") if len(session) > 0 else None
        user = eTree.XML(sysactions.get_user_information(user_id)) if user_id is not None else None
        user = user.find(".//user") if user is not None else None
        user_level = int(user.get("Level")) if user is not None else None

        sale_lines = order_xml.findall(".//SaleLine")

        return Order(order_xml, sale_lines, user_level)

    @staticmethod
    def get_order_max_discount_amount(pos_id):
        # type: (int) -> float

        model = sysactions.get_model(pos_id)
        order_xml = sysactions.get_current_order(model)

        if order_xml is None:
            return 0

        due_amount = float(order_xml.get("dueAmount", 0))
        sale_line_count = len(order_xml.findall(".//SaleLine"))

        return due_amount - 0.01 * sale_line_count

    @staticmethod
    def get_benefits_to_apply(model):
        # type: (eTree) -> List

        try:
            current_order = get_current_order(model)
            value = current_order.find(".//OrderProperty[@key=\"BENEFIT_LIST\"]").get("value")
            return loads(value)
        except OrderTakerException:
            pass
        except AttributeError:
            pass
        return []

    @staticmethod
    def get_benefits_to_apply_by_id(model, benefit_id):
        # type: (eTree, int) -> List

        benefits_to_apply = NDiscountRepository.get_benefits_to_apply(model)
        matching_benefits = []

        for raw_benefit in benefits_to_apply:
            benefit_str = str(raw_benefit.get("benefit"))

            try:
                benefit_json_id = loads(benefit_str).get("id")
            except Exception as _:
                benefit_json_id = None

            if benefit_id == benefit_str or benefit_id == benefit_json_id:
                matching_benefits.append(raw_benefit)

        return matching_benefits

    @staticmethod
    def set_benefits_to_apply(benefits, pos_ot):
        # type: (str, OrderTaker) -> None

        benefits = dumps(benefits) if benefits else "clear"
        pos_ot.setOrderCustomProperty("BENEFIT_LIST", benefits, "")

    @staticmethod
    def delete_benefit_to_apply(benefit_id, pos_ot, model):
        # type: (str, OrderTaker, eTree) -> None

        benefits_to_apply = NDiscountRepository.get_benefits_to_apply(model)
        benefits_to_apply_after_deletion = []

        for raw_benefit in benefits_to_apply:
            benefit_str = str(raw_benefit.get("benefit"))
            try:
                benefit_json_id = loads(benefit_str).get("id")
            except Exception as _:
                benefit_json_id = None

            if benefit_id != benefit_str and benefit_id != benefit_json_id:
                benefits_to_apply_after_deletion.append(raw_benefit)

        NDiscountRepository.set_benefits_to_apply(benefits_to_apply_after_deletion, pos_ot)

    @staticmethod
    def add_benefit_to_apply(benefit, model, pos_ot, burnt_items={}, added_sale_lines=[], promotion_tender_amount=0):
        # type: (str, eTree, OrderTaker, dict, list, float) -> None

        old_benefits = NDiscountRepository.get_benefits_to_apply(model)
        new_benefits = [dict(benefit=benefit,
                             burnt_items=burnt_items,
                             added_sale_lines=added_sale_lines,
                             promotion_tender_amount=promotion_tender_amount)]
        data = dumps(old_benefits + new_benefits)
        pos_ot.setOrderCustomProperty("BENEFIT_LIST", data, "")

    @staticmethod
    def add_applied_benefit_entry(entry, order, pos_ot):
        # type: (AppliedBenefitEntry, Order, OrderTaker) -> None

        data = dumps(loads(Order.get_applied_benefits_json(order)) + [loads(entry.to_json())])
        pos_ot.setOrderCustomProperty("BENEFIT", data, "")

    @staticmethod
    def _apply_discount_by_items(action, order, pos_ot, available_discount_ids, use_percentage=False):
        # type: (Action, Order, OrderTaker, set, bool) -> tuple[list[int], dict]

        applied_discounts = []
        items_to_apply_discount = NDiscountRepository._get_items_to_apply_discount(action)

        for sale_line in order.sale_lines:
            discount_list = items_to_apply_discount.get(int(sale_line.item_id))
            if discount_list is None:
                continue

            remaining_sale_line_qty = sale_line.qty
            discount_counter = 0
            amount = 0

            while remaining_sale_line_qty > 0 and discount_counter < len(discount_list):
                selected_discount = discount_list[discount_counter]
                quantity_to_be_removed = min(remaining_sale_line_qty, selected_discount["quantity"])
                total_value_to_remove = sale_line.unit_price * quantity_to_be_removed

                remaining_sale_line_qty -= quantity_to_be_removed
                selected_discount["quantity"] -= quantity_to_be_removed

                if use_percentage:
                    amount_to_add = total_value_to_remove * (selected_discount["amount"] / 100)
                else:
                    amount_to_add = quantity_to_be_removed * selected_discount["amount"]

                amount += min(amount_to_add, total_value_to_remove)

                if selected_discount["quantity"] == 0:
                    del discount_list[discount_counter]
                discount_counter += 1

            amount = min(float(amount), NDiscountRepository.get_order_max_discount_amount(order.pos_id))
            if amount > 0:
                discount_id = available_discount_ids.pop()
                pos_ot.applyDiscount(discount_id, amount, sale_line.line_number, sale_line.context, sale_line.level,
                                     sale_line.item_id)
                applied_discounts.append(discount_id)

        return applied_discounts, {}

    @staticmethod
    def _get_items_to_apply_discount(action):
        items_to_apply_discount = {}

        for entry in action.value:
            key = int(entry.get("item", -1))
            items_to_apply_discount[key] = items_to_apply_discount.get(key, []) + \
                                           [{
                                               "quantity": int(entry.get("quantity", 0)),
                                               "amount": float(entry.get("amount", entry.get("percentage", 0)))
                                           }]

        for key in items_to_apply_discount.keys():
            items_to_apply_discount[key].sort(key=lambda el: el.get("amount"), reverse=True)

        return items_to_apply_discount

    @staticmethod
    def apply_discount_amount_by_items(action, order, posot, available_discount_ids):
        # type: (Action, Order, OrderTaker, set) -> tuple[list[int], dict]

        return NDiscountRepository._apply_discount_by_items(action, order, posot, available_discount_ids)

    @staticmethod
    def apply_discount_percentage_by_items(action, order, posot, available_discount_ids):
        # type: (Action, Order, OrderTaker, set) -> tuple[list[int], dict]

        return NDiscountRepository._apply_discount_by_items(action, order, posot, available_discount_ids, True)

    @staticmethod
    def apply_discount_amount_on_total(action, order, pos_ot, available_discount_ids):
        # type: (Action, Order, OrderTaker, set) -> tuple[list[int], dict]

        return NDiscountRepository.apply_discount_on_total(action, order, pos_ot, available_discount_ids)

    @staticmethod
    def apply_discount_percentage_on_total(action, order, pos_ot, available_discount_ids):
        # type: (Action, Order, OrderTaker, set) -> tuple[list[int], dict]

        return NDiscountRepository.apply_discount_on_total(action, order, pos_ot, available_discount_ids, True)

    @staticmethod
    def apply_discount_on_total(action, order, pos_ot, available_discount_ids, use_percentage=False):
        # type: (Action, Order, OrderTaker, set, bool) -> tuple[list[int], dict]

        amount = order.total_amount * (float(action.value) / 100) if use_percentage else float(action.value)
        amount = min(float(amount), NDiscountRepository.get_order_max_discount_amount(order.pos_id))
        if amount > 0:
            discount_id = available_discount_ids.pop()
            pos_ot.applyDiscount(discount_id, amount, forcebyitem=1)
            return [discount_id], dict()
        return [], dict()

    @staticmethod
    def execute_action(action, order, pos_ot, available_discount_ids):
        # type: (Action, Order, OrderTaker, set) -> tuple[list[int], dict]

        if action.name == ActionTypes.discountAmountOnTotal.value:
            return NDiscountRepository.apply_discount_amount_on_total(action, order, pos_ot, available_discount_ids)
        elif action.name == ActionTypes.discountPercentageOnTotal.value:
            return NDiscountRepository.apply_discount_percentage_on_total(action, order, pos_ot, available_discount_ids)
        elif action.name == ActionTypes.discountAmountByItems.value:
            return NDiscountRepository.apply_discount_amount_by_items(action, order, pos_ot, available_discount_ids)
        elif action.name == ActionTypes.discountPercentageByItems.value:
            return NDiscountRepository.apply_discount_percentage_by_items(action, order, pos_ot, available_discount_ids)
        return [], dict()
