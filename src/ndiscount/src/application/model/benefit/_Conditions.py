from datetime import datetime

from application.model.benefit._RequiredItemOnSale import RequiredItemOnSale
from application.model.benefit._ValidHours import ValidHours
from iso8601 import iso8601


class Conditions(object):
    def __init__(self,
                 user_min_level,
                 unique_for_sale,
                 single_use,
                 burn_items,
                 ignore_burned_items,
                 pod_type,
                 min_sale_amount,
                 max_sale_amount,
                 valid_start_period,
                 valid_end_period,
                 valid_hours,
                 valid_days,
                 required_items_on_sale
                 ):
        # type: (int, bool, bool, bool, bool, list[str], float, float, datetime, datetime, ValidHours, list[int], list[RequiredItemOnSale]) -> None
        self.user_min_level = user_min_level
        self.unique_for_sale = unique_for_sale
        self.single_use = single_use or ignore_burned_items
        self.burn_items = burn_items
        self.ignore_burned_items = ignore_burned_items
        self.pod_type = pod_type
        self.min_sale_amount = min_sale_amount
        self.max_sale_amount = max_sale_amount
        self.valid_start_period = valid_start_period
        self.valid_end_period = valid_end_period
        self.valid_hours = valid_hours
        self.valid_days = valid_days
        self.required_items_on_sale = required_items_on_sale

    @staticmethod
    def from_self_stored_json(obj):
        return Conditions(
            obj.get("user_min_level"),
            bool(obj.get("unique_for_sale")),
            bool(obj.get("single_use")),
            bool(obj.get("burn_items")),
            bool(obj.get("ignore_burned_items")),
            list(obj.get("pod_type")) if obj.get("pod_type") else None,
            obj.get("min_sale_amount"),
            obj.get("max_sale_amount"),
            iso8601.parse_date(obj.get("valid_start_period")) if obj.get(
                "valid_start_period") else None,
            iso8601.parse_date(obj.get("valid_end_period")) if obj.get(
                "valid_end_period") else None,
            ValidHours(obj["valid_hours"].get("start_hour"), obj["valid_hours"].get("end_hour")),
            list(obj.get("valid_days")) if obj.get("valid_days") else None,
            [RequiredItemOnSale(x) for x in obj.get("required_items_on_sale", [])]
        )

    @staticmethod
    def from_benefit_json(obj):
        user_min_level = obj.get("userMinLevel")
        unique_for_sale = bool(obj.get("uniqueForSale"))
        single_use = bool(obj.get("singleUse"))
        burn_items = bool(obj.get("burnItems"))
        ignore_burned_items = bool(obj.get("ignoreBurnedItems"))
        pod_type = list(obj.get("podType")) if obj.get("podType") else None
        min_sale_amount = float(obj.get("minSaleAmount")) if obj.get("minSaleAmount") else None
        max_sale_amount = float(obj.get("maxSaleAmount")) if obj.get("maxSaleAmount") else None
        valid_start_period = iso8601.parse_date(obj.get("validStartPeriod")) if obj.get(
            "validStartPeriod") else None
        valid_end_period = iso8601.parse_date(obj.get("validEndPeriod")) if obj.get("validEndPeriod") else None
        valid_hours = ValidHours(obj["validHours"].get("startHour"), obj["validHours"].get("endHour")) if obj.get(
            "validHours") else ValidHours(None, None)
        valid_days = list(obj.get("validDays")) if obj.get("validDays") else None
        required_items_on_sale = [RequiredItemOnSale(x) for x in obj.get("requiredItemsOnSale", [])]

        return Conditions(
            user_min_level=user_min_level,
            unique_for_sale=unique_for_sale,
            single_use=single_use,
            burn_items=burn_items,
            ignore_burned_items=ignore_burned_items,
            pod_type=pod_type,
            min_sale_amount=min_sale_amount,
            max_sale_amount=max_sale_amount,
            valid_start_period=valid_start_period,
            valid_end_period=valid_end_period,
            valid_hours=valid_hours,
            valid_days=valid_days,
            required_items_on_sale=required_items_on_sale
        )
