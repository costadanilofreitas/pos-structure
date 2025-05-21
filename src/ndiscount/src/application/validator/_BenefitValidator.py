from abc import ABCMeta
from datetime import datetime
from xml.etree import cElementTree as eTree
from xml.etree.cElementTree import Element

import sysactions
from application.model import BenefitExpiredOrInactiveException, PodTypeNotValidException, \
    InsufficientSaleAmountException, ExcessiveSaleAmountException, UserLevelNotAllowedException, \
    MissingItemsException, CustomBenefitAlreadyAppliedException
from application.model.benefit import Benefit, AppliedBenefitEntry
from application.model.order import Order
from iso8601 import iso8601


# todo - export validation
class BenefitValidator:
    __metaclass__ = ABCMeta

    @staticmethod
    def is_benefit_valid_now(benefit):
        # type: (Benefit) -> None
        conditions = benefit.conditions
        valid_hours = conditions.valid_hours

        now = datetime.now().isoformat().split("T")[1]
        if valid_hours.start_hour is not None and now < valid_hours.start_hour:
            raise BenefitExpiredOrInactiveException('NDISCOUNT_START_HOUR')
        if valid_hours.end_hour is not None and now > valid_hours.end_hour:
            raise BenefitExpiredOrInactiveException('NDISCOUNT_END_HOUR')

        now = datetime.now()
        if conditions.valid_days is not None and str(now.weekday() + 1) not in conditions.valid_days:
            raise BenefitExpiredOrInactiveException('NDISCOUNT_VALID_DAYS')

        now = iso8601.parse_date(datetime.utcnow().isoformat())
        if conditions.valid_start_period is not None and now < conditions.valid_start_period:
            raise BenefitExpiredOrInactiveException('NDISCOUNT_START_PERIOD')
        if conditions.valid_end_period is not None and now > conditions.valid_end_period:
            raise BenefitExpiredOrInactiveException('NDISCOUNT_END_PERIOD')

    @staticmethod
    def _missing_items_on_order(benefit, order, burnt_items):
        # type: (Benefit, Order, dict) -> int
        sale_lines = order.sale_lines
        conditions = benefit.conditions

        required_items_on_sale = {}

        for item in conditions.required_items_on_sale:
            key = "{};{}".format(item.context if item.context else 'any', str(item.item_id))
            required_items_on_sale[key] = item.quantity

        for sale_line in sale_lines:
            context = sale_line.context
            quantity = sale_line.qty

            quantity -= 0 if conditions.ignore_burned_items else int(burnt_items.get(sale_line.key, 0))

            for item_index in required_items_on_sale.keys():
                required_item_context, required_item_id = item_index.split(';')

                if int(sale_line.item_id) != int(required_item_id):
                    continue

                if required_item_context == 'any' or required_item_context in context:
                    t_quantity = quantity
                    quantity = max(0, quantity - required_items_on_sale[item_index])
                    required_items_on_sale[item_index] = max(0, required_items_on_sale[item_index] - t_quantity)

        return sum(required_items_on_sale.values())

    @staticmethod
    def validate_benefit_for_order(benefit, order, benefits_to_apply, burnt_items):
        # type: (Benefit, Order, list, dict) -> bool
        conditions = benefit.conditions

        BenefitValidator.is_benefit_valid_now(benefit)
        if len(benefits_to_apply) > 0 and conditions.unique_for_sale:
            raise CustomBenefitAlreadyAppliedException('NDISCOUNT_ERROR_UNIQUE_FOR_SALE')
        if conditions.min_sale_amount is not None and order.total_amount < conditions.min_sale_amount:
            raise InsufficientSaleAmountException('NDISCOUNT_ERROR_MIN_SALE_AMOUNT')
        if conditions.max_sale_amount is not None and order.total_amount > conditions.max_sale_amount:
            raise ExcessiveSaleAmountException('NDISCOUNT_ERROR_MAX_SALE_AMOUNT')
        if BenefitValidator._missing_items_on_order(benefit, order, burnt_items) > 0:
            raise MissingItemsException('NDISCOUNT_ERROR_REQUIRED_ITEMS_ON_SALE')

        return True

    @staticmethod
    def validate_benefit_for_model(benefit, model):
        # type: (Benefit, Element) -> bool
        conditions = benefit.conditions

        BenefitValidator.is_benefit_valid_now(benefit)

        if conditions.pod_type:
            pod_type = None
            try:
                pod_type = model.find(".//WorkingMode").get("podType")
            finally:
                if pod_type is None or pod_type not in conditions.pod_type:
                    raise PodTypeNotValidException('NDISCOUNT_ERROR_POD_TYPE')

        if conditions.user_min_level is not None:
            user_level = None
            try:
                order_xml = sysactions.get_current_order(model)
                session = [v for v in order_xml.get("sessionId", "").split(",") if v.startswith("user=")]
                user_id = session[0].replace("user=", "") if len(session) > 0 else None
                user = eTree.XML(sysactions.get_user_information(user_id)) if user_id is not None else None
                user = user.find(".//user") if user is not None else None
                user_level = int(user.get("Level")) if user is not None else None
            finally:
                if user_level is None or user_level < conditions.user_min_level:
                    raise UserLevelNotAllowedException('NDISCOUNT_ERROR_USER_MIN_LEVEL')

        return True

    @staticmethod
    def validate_applied_benefit(applied_benefit, order):
        # type: (AppliedBenefitEntry, Order) -> bool

        for sale_line in order.sale_lines:
            if int(sale_line.qty) == int(sale_line.level) == 0 and \
                    sale_line.line_number in applied_benefit.added_sale_lines:
                return False

        return True
